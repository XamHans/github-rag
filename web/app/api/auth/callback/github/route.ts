import { db } from '@/lib/db';
import { accounts, users } from '@/modules/user/schema';
import { eq } from 'drizzle-orm';
import { NextRequest, NextResponse } from 'next/server';

// Helper function for logging
function log(message: string, data?: any) {
    console.log(`[GitHub OAuth] ${message}`, data ? JSON.stringify(data, null, 2) : '');
}

export async function GET(request: NextRequest) {
    log('Received callback from GitHub OAuth');

    const { searchParams } = new URL(request.url);
    const code = searchParams.get('code');
    log('Received authorization code', { code });

    if (!code) {
        log('No authorization code received from GitHub');
        return NextResponse.json({ message: 'Missing authorization code' }, { status: 400 });
    }

    try {
        log('Exchanging temporary code for access token');
        const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
            },
            body: JSON.stringify({
                client_id: process.env.AUTH_GITHUB_ID,
                client_secret: process.env.AUTH_GITHUB_SECRET,
                code,
            }),
        });

        const tokenData = await tokenResponse.json();
        log('Received token data', { tokenData: { ...tokenData } });

        if (!tokenData.access_token) {
            log('Failed to obtain access token from GitHub');
            return NextResponse.json({ message: 'Failed to obtain access token' }, { status: 400 });
        }

        log('Successfully obtained access token');

        log('Fetching user data from GitHub');
        const userResponse = await fetch('https://api.github.com/user', {
            headers: {
                Authorization: `Bearer ${tokenData.access_token}`,
            },
        });

        const userData = await userResponse.json();

        const existingUser = await db.select().from(users).where(eq(users.github_id, userData.id)).execute();

        let userId: string;

        if (existingUser.length > 0) {
            userId = existingUser[0].id;
            log('Existing user found', { userId });
        } else {
            log('Creating new user');
            const [newUser] = await db.insert(users).values({
                id: userData.node_id,
                name: userData.name,
                email: userData.email ?? '',
                image: userData.avatar_url,
                github_id: userData.id.toString(),
            }).returning({ id: users.id });

            userId = newUser.id;
            log('New user created', { userId });
        }

        log('Creating or updating account');
        await db.insert(accounts).values({
            userId,
            type: 'oauth',
            provider: 'github',
            providerAccountId: userData.id.toString(),
            access_token: tokenData.access_token,
            token_type: tokenData.token_type,
            scope: tokenData.scope,
        }).onConflictDoUpdate({
            target: [accounts.provider, accounts.providerAccountId],
            set: {
                access_token: tokenData.access_token,
                token_type: tokenData.token_type,
                scope: tokenData.scope,
            },
        });
        log('Account created or updated successfully');

        log('OAuth flow completed successfully');
        return NextResponse.redirect(new URL('/onboarding', request.url));
    } catch (error) {
        log('Error in GitHub OAuth callback handler', error);
        if (error instanceof Error) {
            log('Error details', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
        }
        return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
    }
}