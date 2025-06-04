const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

const CONFIG_PATH = '/home/ender/.npm-global/lib/node_modules/spotify-mcp-server/spotify-config.json';

// Load Spotify config with error handling
let config;
try {
    config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
} catch (error) {
    console.error('❌ Could not load Spotify config:', error.message);
    console.log('🔧 Using fallback configuration...');
    config = {
        client_id: 'b207314de9ad443bb6b90d12a5d68243',
        client_secret: '1e4f616a41bc406e8a43bc852f1597ac',
        redirect_uri: 'http://127.0.0.1:8888/callback'
    };
}

const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);
    
    if (parsedUrl.pathname === '/callback') {
        const { code, state, error } = parsedUrl.query;
        
        console.log('🔄 Callback received:', { code: code ? 'PRESENT' : 'MISSING', state, error });
        
        if (error) {
            console.error('❌ Authorization error:', error);
            res.writeHead(400, { 'Content-Type': 'text/html' });
            res.end(`
                <h1>Authorization Error</h1>
                <p><strong>Error:</strong> ${error}</p>
                <p>Please try the authorization process again.</p>
                <button onclick="window.close()">Close Window</button>
            `);
            return;
        }
        
        if (!code) {
            console.error('❌ No authorization code received');
            res.writeHead(400, { 'Content-Type': 'text/html' });
            res.end(`
                <h1>Error</h1>
                <p>No authorization code received from Spotify.</p>
                <p>Please try the authorization process again.</p>
                <button onclick="window.close()">Close Window</button>
            `);
            return;
        }
        
        try {
            console.log('🔄 Exchanging code for tokens...');
            // Exchange code for tokens
            const tokenData = await exchangeCodeForTokens(code);
            
            console.log('✅ Token exchange successful');
            
            // Update config file with tokens
            const updatedConfig = {
                ...config,
                accessToken: tokenData.access_token,
                refreshToken: tokenData.refresh_token,
                expiresAt: Date.now() + (tokenData.expires_in * 1000)
            };
            
            try {
                fs.writeFileSync(CONFIG_PATH, JSON.stringify(updatedConfig, null, 2));
                console.log('✅ Tokens saved to config file');
            } catch (writeError) {
                console.error('❌ Failed to save config:', writeError.message);
            }
            
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(`
                <html>
                <head><title>Spotify Auth Success</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #1db954;">✅ Success!</h1>
                    <p>Spotify authentication completed successfully.</p>
                    <p>You can now close this window and use the Spotify MCP server.</p>
                    <button onclick="window.close()" style="padding: 10px 20px; background: #1db954; color: white; border: none; border-radius: 5px;">Close Window</button>
                    <script>setTimeout(() => window.close(), 5000);</script>
                </body>
                </html>
            `);
            
            console.log('🎉 Authentication successful! Tokens saved to config file.');
            
            // Close server after successful auth
            setTimeout(() => {
                console.log('🔚 Closing OAuth server...');
                server.close();
                process.exit(0);
            }, 7000);
            
        } catch (error) {
            console.error('❌ Token exchange error:', error);
            res.writeHead(500, { 'Content-Type': 'text/html' });
            res.end(`
                <html>
                <head><title>Spotify Auth Error</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #e22134;">❌ Error</h1>
                    <p>Failed to exchange code for tokens:</p>
                    <p><strong>${error.message}</strong></p>
                    <p>Please try the authorization process again.</p>
                    <button onclick="window.close()" style="padding: 10px 20px; background: #e22134; color: white; border: none; border-radius: 5px;">Close Window</button>
                </body>
                </html>
            `);
        }
    } else {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>Not Found</h1>');
    }
});

async function exchangeCodeForTokens(code) {
    const tokenUrl = 'https://accounts.spotify.com/api/token';
    const clientId = config.client_id || config.clientId;
    const clientSecret = config.client_secret || config.clientSecret;
    const redirectUri = config.redirect_uri || config.redirectUri;
    
    console.log('🔑 Using credentials:', { 
        clientId: clientId ? 'SET' : 'MISSING', 
        clientSecret: clientSecret ? 'SET' : 'MISSING',
        redirectUri 
    });
    
    if (!clientId || !clientSecret) {
        throw new Error('Missing Spotify client credentials');
    }
    
    const credentials = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
    
    const params = new URLSearchParams({
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: redirectUri
    });
    
    console.log('📤 Token exchange request:', { tokenUrl, redirectUri });
    
    const response = await fetch(tokenUrl, {
        method: 'POST',
        headers: {
            'Authorization': `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: params
    });
    
    console.log('📥 Token response status:', response.status);
    
    if (!response.ok) {
        const errorData = await response.text();
        console.error('❌ Token exchange error response:', errorData);
        throw new Error(`Token exchange failed: ${response.status} ${errorData}`);
    }
    
    const tokenData = await response.json();
    console.log('✅ Token data received:', { 
        access_token: tokenData.access_token ? 'PRESENT' : 'MISSING',
        refresh_token: tokenData.refresh_token ? 'PRESENT' : 'MISSING',
        expires_in: tokenData.expires_in 
    });
    
    return tokenData;
}

const PORT = 8888;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`🎵 Spotify OAuth server running on http://127.0.0.1:${PORT}`);
    console.log('\n📋 To authenticate, visit this URL:');
    
    const clientId = config.client_id || config.clientId;
    const redirectUri = config.redirect_uri || config.redirectUri;
    
    const authUrl = `https://accounts.spotify.com/authorize?` + new URLSearchParams({
        client_id: clientId,
        response_type: 'code',
        redirect_uri: redirectUri,
        scope: 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-modify-private playlist-modify-public user-library-read user-library-modify user-read-recently-played',
        state: Math.random().toString(36).substring(7),
        show_dialog: true
    });
    
    console.log('\n🔗', authUrl);
    console.log('\n⏳ Waiting for authorization...');
});