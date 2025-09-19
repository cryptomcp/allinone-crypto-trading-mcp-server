#!/usr/bin/env node

const algoliasearch = require('algoliasearch');

const main = async () => {
  try {
    const client = algoliasearch(process.env.ALGOLIA_APP_ID, process.env.ALGOLIA_API_KEY);
    const index = client.initIndex(process.env.ALGOLIA_INDEX_NAME);
    
    console.log('✅ Connected to Algolia index:', process.env.ALGOLIA_INDEX_NAME);
    
    // Basic documentation records
    const records = [
      {
        objectID: 'home',
        title: 'All-in-One Crypto Trading MCP Server',
        content: 'Complete cryptocurrency trading and analytics platform built on the Model Context Protocol (MCP). Multi-exchange support, AI signals, blockchain integrations.',
        url: '/',
        type: 'page'
      },
      {
        objectID: 'getting-started',
        title: 'Getting Started',
        content: 'Setup guide for the crypto trading MCP server. Installation, configuration, and first trade walkthrough.',
        url: '/getting-started',
        type: 'guide'
      },
      {
        objectID: 'features-trading',
        title: 'Trading Features',
        content: 'Multi-exchange support with Binance, Coinbase Pro, Kraken, Bybit, OKX. Smart order routing, portfolio management, risk controls.',
        url: '/features/trading',
        type: 'feature'
      },
      {
        objectID: 'features-blockchain',
        title: 'Blockchain Integration',
        content: '8+ blockchain networks: Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, Avalanche, Solana. DEX analytics, cross-chain bridges.',
        url: '/features/blockchain',
        type: 'feature'
      },
      {
        objectID: 'features-ai-signals',
        title: 'AI Trading Signals',
        content: 'Machine learning powered trading recommendations, market sentiment analysis, technical indicators.',
        url: '/features/ai-signals',
        type: 'feature'
      },
      {
        objectID: 'features-telegram-bot',
        title: 'Telegram Bot',
        content: 'Full trading interface via Telegram. Mobile trading, portfolio tracking, real-time alerts.',
        url: '/features/telegram-bot',
        type: 'feature'
      },
      {
        objectID: 'api-reference',
        title: 'API Reference',
        content: 'Complete API documentation for trading, portfolio management, blockchain interactions, AI signals.',
        url: '/api-reference',
        type: 'documentation'
      },
      {
        objectID: 'deployment-docker',
        title: 'Docker Deployment',
        content: 'Docker containerization guide, multi-stage builds, production deployment with monitoring.',
        url: '/deployment/docker',
        type: 'guide'
      },
      {
        objectID: 'deployment-production',
        title: 'Production Deployment',
        content: 'AWS, GCP, Azure deployment guides. Cloud infrastructure, scaling, monitoring, backup strategies.',
        url: '/deployment/production',
        type: 'guide'
      }
    ];
    
    console.log(`📝 Indexing ${records.length} records...`);
    
    // Clear existing index
    await index.clearObjects();
    console.log('🗑️  Cleared existing index');
    
    // Add new records
    const result = await index.saveObjects(records);
    console.log('✅ Successfully indexed', records.length, 'records');
    console.log('📊 Index status:', result.objectIDs.length, 'objects created');
    
  } catch (error) {
    console.error('❌ Indexing failed:', error.message);
    process.exit(1);
  }
};

main();