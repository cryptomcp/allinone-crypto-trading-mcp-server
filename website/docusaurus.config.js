// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'All-in-One Crypto Trading MCP Server',
  tagline: 'Complete cryptocurrency trading and analytics platform built on the Model Context Protocol (MCP)',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://allinonecryptomcp.dev',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'cryptomcp', 
  projectName: 'allinone-crypto-trading-mcp-server',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: false,
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/cryptomcp/allinone-crypto-trading-mcp-server/tree/main/docs/',
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        gtag: {
          trackingID: 'G-M34MW67V3X',
          anonymizeIP: true,
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/crypto-mcp-social-card.svg',
      navbar: {
        title: 'CryptoMCP',
        logo: {
          alt: 'CryptoMCP Logo',
          src: 'img/logo.svg',
          srcDark: 'img/logo-dark.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            to: '/features/trading',
            label: 'Features',
            position: 'left',
          },
          {
            to: '/api-reference',
            label: 'API Reference',
            position: 'left',
          },
          {
            href: 'https://github.com/cryptomcp/allinone-crypto-trading-mcp-server',
            label: 'GitHub',
            position: 'right',
          },
          {
            href: 'https://t.me/web3botsupport',
            label: 'Telegram',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/getting-started',
              },
              {
                label: 'API Reference',
                to: '/api-reference',
              },
              {
                label: 'Tutorials',
                to: '/tutorials/installation',
              },
            ],
          },
          {
            title: 'Features',
            items: [
              {
                label: 'Trading',
                to: '/features/trading',
              },
              {
                label: 'Blockchain',
                to: '/features/blockchain',
              },
              {
                label: 'AI Signals',
                to: '/features/ai-signals',
              },
              {
                label: 'Risk Management',
                to: '/features/risk-management',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Telegram',
                href: 'https://t.me/web3botsupport',
              },
              {
                label: 'Support Chat',
                href: 'https://t.me/web3botsupport',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/cryptomcp',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/cryptomcp/allinone-crypto-trading-mcp-server',
              },
            ],
          },
          {
            title: 'Support',
            items: [
              {
                label: 'Support Center',
                href: 'mailto:support@allinonecryptomcp.dev',
              },
              {
                label: 'Enterprise',
                href: 'mailto:enterprise@allinonecryptomcp.dev',
              },
              {
                label: 'Security',
                href: 'mailto:security@allinonecryptomcp.dev',
              },
              {
                label: 'Bug Bounty',
                href: 'mailto:security@allinonecryptomcp.dev',
              },
            ],
          },
        ],
        copyright: `© ${new Date().getFullYear()} CryptoMCP Team. All rights reserved. Built with ❤️ for the crypto community.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['bash', 'docker', 'python', 'javascript', 'yaml', 'json'],
      },
      
      // 🔍 ALGOLIA SEARCH CONFIGURATION
      // Note: Will be automatically configured after GitHub Pages deployment
      algolia: {
        // The application ID provided by Algolia
        appId: 'YOUR_ALGOLIA_APP_ID',
        
        // Public API key: it is safe to commit it
        apiKey: 'YOUR_ALGOLIA_SEARCH_API_KEY',
        
        indexName: 'allinonecryptomcp-docs',
        
        // Optional: see doc section below
        contextualSearch: true,
        
        // Optional: Specify domains where the navigation should occur through window.location instead on history.push
        externalUrlRegex: 'external\\.com|domain\\.com',
        
        // Optional: Replace suggestion intent default search term
        replaceSearchResultPathname: {
          from: '/docs/', // or as RegExp: /\/docs\//
          to: '/',
        },
        
        // Optional: Algolia search parameters
        searchParameters: {
          facetFilters: ['language:en'],
          hitsPerPage: 10,
        },
        
        // Optional: path for search page that enabled by default (`false` to disable it)
        searchPagePath: 'search',
        
        // Optional: whether to use insights/analytics
        insights: false,
        
        // Optional: search placeholder
        placeholder: 'Search documentation...',
        
        // Optional: translations for better UX
        translations: {
          button: {
            buttonText: 'Search',
            buttonAriaLabel: 'Search documentation',
          },
          modal: {
            searchBox: {
              resetButtonTitle: 'Clear search',
              resetButtonAriaLabel: 'Clear search',
              cancelButtonText: 'Cancel',
              cancelButtonAriaLabel: 'Cancel',
            },
            startScreen: {
              recentSearchesTitle: 'Recent searches',
              noRecentSearchesText: 'No recent searches',
              saveRecentSearchButtonTitle: 'Save this search',
              removeRecentSearchButtonTitle: 'Remove from history',
              favoriteSearchesTitle: 'Favorites',
              removeFavoriteSearchButtonTitle: 'Remove from favorites',
            },
            errorScreen: {
              titleText: 'Unable to fetch results',
              helpText: 'Check your network connection and try again.',
            },
            footer: {
              selectText: 'to select',
              navigateText: 'to navigate', 
              closeText: 'to close',
              searchByText: 'Search powered by',
            },
            noResultsScreen: {
              noResultsText: 'No results found for',
              suggestedQueryText: 'Try searching for',
              reportMissingResultsText: 'Missing results?',
              reportMissingResultsLinkText: 'Report it here',
            },
          },
        },
      },
      
      announcementBar: {
        id: 'solana_trading_bot',
        content: '🚀 <strong>Live Trading Bot Available!</strong> Experience this MCP server in action at <a target="_blank" rel="noopener noreferrer" href="https://solanatrade.bot" style="color: #34d399; font-weight: bold; text-decoration: underline;">solanatrade.bot</a> - Built with this exact repository! 📈✨',
        backgroundColor: '#1e293b',
        textColor: '#ffffff',
        isCloseable: false,
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

module.exports = config;