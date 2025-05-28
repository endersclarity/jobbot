const { chromium, firefox, webkit } = require('playwright');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
    url: 'https://indeed.com',
    timeout: 30000,
    screenshotDir: './screenshots',
    browsers: ['chromium', 'firefox', 'webkit'],
    modes: [
        { name: 'headless', headless: true },
        { name: 'headed', headless: false }
    ]
};

// Ensure screenshot directory exists
if (!fs.existsSync(TEST_CONFIG.screenshotDir)) {
    fs.mkdirSync(TEST_CONFIG.screenshotDir, { recursive: true });
}

async function testIndeedAccess(browserType, mode) {
    const testName = `${browserType}-${mode.name}`;
    console.log(`\n🧪 Testing Indeed.com access with ${testName}...`);
    
    let browser;
    let context;
    let page;
    
    try {
        // Launch browser
        const browserEngine = browserType === 'chromium' ? chromium : 
                             browserType === 'firefox' ? firefox : webkit;
        
        browser = await browserEngine.launch({
            headless: mode.headless,
            slowMo: mode.headless ? 0 : 1000, // Slow down for visual testing
            args: [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
        });

        // Create context with realistic settings
        context = await browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            locale: 'en-US',
            timezoneId: 'America/New_York'
        });

        page = await context.newPage();

        // Set up request/response monitoring
        const responses = [];
        page.on('response', response => {
            responses.push({
                url: response.url(),
                status: response.status(),
                statusText: response.statusText()
            });
        });

        console.log(`  📍 Navigating to ${TEST_CONFIG.url}...`);
        
        // Navigate to Indeed.com
        const response = await page.goto(TEST_CONFIG.url, {
            waitUntil: 'networkidle',
            timeout: TEST_CONFIG.timeout
        });

        // Get page info
        const status = response.status();
        const title = await page.title();
        const url = page.url();
        
        console.log(`  📊 Response Status: ${status}`);
        console.log(`  📝 Page Title: "${title}"`);
        console.log(`  🔗 Final URL: ${url}`);

        // Check for common blocking indicators
        const pageText = await page.textContent('body').catch(() => '');
        const isBlocked = 
            status === 403 ||
            status === 429 ||
            title.toLowerCase().includes('access denied') ||
            title.toLowerCase().includes('blocked') ||
            pageText.toLowerCase().includes('blocked') ||
            pageText.toLowerCase().includes('access denied') ||
            pageText.toLowerCase().includes('robot');

        console.log(`  🚫 Blocked: ${isBlocked ? 'YES' : 'NO'}`);

        // Take screenshot
        const screenshotPath = path.join(TEST_CONFIG.screenshotDir, `indeed-${testName}-${Date.now()}.png`);
        await page.screenshot({
            path: screenshotPath,
            fullPage: true
        });
        console.log(`  📸 Screenshot saved: ${screenshotPath}`);

        // Test basic interaction
        try {
            const searchBox = await page.locator('input[name="q"], input[id="text-input-what"]').first();
            if (await searchBox.isVisible({ timeout: 5000 })) {
                console.log(`  ✅ Search box found and visible`);
                await searchBox.fill('software engineer');
                console.log(`  ✅ Successfully typed in search box`);
            } else {
                console.log(`  ❌ Search box not found or not visible`);
            }
        } catch (error) {
            console.log(`  ❌ Search box interaction failed: ${error.message}`);
        }

        // Analyze responses
        const mainResponse = responses.find(r => r.url === TEST_CONFIG.url || r.url === TEST_CONFIG.url + '/');
        const errorResponses = responses.filter(r => r.status >= 400);
        
        console.log(`  📡 Total responses: ${responses.length}`);
        console.log(`  🔴 Error responses: ${errorResponses.length}`);
        
        if (errorResponses.length > 0) {
            console.log(`  🔍 Error details:`);
            errorResponses.slice(0, 5).forEach(r => {
                console.log(`    - ${r.status} ${r.statusText}: ${r.url}`);
            });
        }

        return {
            testName,
            success: !isBlocked && status < 400,
            status,
            title,
            url,
            isBlocked,
            screenshotPath,
            responseCount: responses.length,
            errorCount: errorResponses.length,
            canInteract: pageText.length > 100 // Basic content check
        };

    } catch (error) {
        console.log(`  ❌ Test failed: ${error.message}`);
        return {
            testName,
            success: false,
            error: error.message
        };
    } finally {
        if (page) await page.close();
        if (context) await context.close();
        if (browser) await browser.close();
    }
}

async function runAllTests() {
    console.log('🚀 Starting Indeed.com Access Test Suite');
    console.log(`📅 Test Time: ${new Date().toISOString()}`);
    
    const results = [];

    for (const browserType of TEST_CONFIG.browsers) {
        for (const mode of TEST_CONFIG.modes) {
            try {
                const result = await testIndeedAccess(browserType, mode);
                results.push(result);
                
                // Wait between tests to avoid rate limiting
                await new Promise(resolve => setTimeout(resolve, 2000));
            } catch (error) {
                console.log(`❌ Failed to run test ${browserType}-${mode.name}: ${error.message}`);
                results.push({
                    testName: `${browserType}-${mode.name}`,
                    success: false,
                    error: error.message
                });
            }
        }
    }

    // Summary
    console.log('\n📋 TEST SUMMARY');
    console.log('================');
    
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);
    const blocked = results.filter(r => r.isBlocked);

    console.log(`✅ Successful: ${successful.length}/${results.length}`);
    console.log(`❌ Failed: ${failed.length}/${results.length}`);
    console.log(`🚫 Blocked: ${blocked.length}/${results.length}`);

    if (successful.length > 0) {
        console.log('\n🎉 Working configurations:');
        successful.forEach(r => {
            console.log(`  - ${r.testName}: Status ${r.status}, Title: "${r.title}"`);
        });
    }

    if (blocked.length > 0) {
        console.log('\n🚫 Blocked configurations:');
        blocked.forEach(r => {
            console.log(`  - ${r.testName}: Status ${r.status}`);
        });
    }

    if (failed.length > 0) {
        console.log('\n❌ Failed configurations:');
        failed.forEach(r => {
            console.log(`  - ${r.testName}: ${r.error || 'Unknown error'}`);
        });
    }

    // Save detailed results
    const reportPath = path.join(TEST_CONFIG.screenshotDir, `test-report-${Date.now()}.json`);
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`\n📊 Detailed report saved: ${reportPath}`);

    // Recommendations
    console.log('\n💡 RECOMMENDATIONS');
    console.log('==================');
    
    if (successful.length === 0) {
        console.log('🔴 All tests failed - Indeed.com may be blocking all automated access');
        console.log('   Consider using residential proxies or different user agents');
    } else if (blocked.length > 0) {
        console.log('🟡 Some configurations are blocked - use successful ones for scraping');
        console.log('   Working configurations can be used for job search automation');
    } else {
        console.log('🟢 All tests passed - Indeed.com access appears to be working');
        console.log('   Previous 403 errors may be specific to job search URLs or rate limiting');
    }

    return results;
}

// Run the tests
if (require.main === module) {
    runAllTests().catch(console.error);
}

module.exports = { runAllTests, testIndeedAccess };