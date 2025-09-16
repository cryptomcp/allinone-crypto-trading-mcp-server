# Deployment Setup Instructions

Follow these steps to deploy your documentation to GitHub Pages using Docusaurus.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd website
npm install
```

### 2. Local Development
```bash
# Start development server
npm start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

### 3. GitHub Pages Deployment

#### Automatic Deployment (Recommended)
The documentation will automatically deploy to GitHub Pages when you push to the main branch. The GitHub Action is already configured in `.github/workflows/deploy-docs.yml`.

#### Manual Deployment
```bash
# Set your GitHub username and repository name
export GIT_USER=your-github-username
export DEPLOYMENT_BRANCH=gh-pages

# Deploy to GitHub Pages
cd website
npm run deploy
```

### 4. Configure Repository Settings

1. Go to your GitHub repository settings
2. Navigate to "Pages" section
3. Set source to "GitHub Actions"
4. The site will be available at: `https://your-username.github.io/allinone-crypto-trading-mcp-server/`

## 📁 Project Structure

```
allinone-crypto-mcp/
├── docs/                          # Documentation source files
│   ├── README.md                   # Main documentation index
│   ├── getting-started.md          # Getting started guide
│   ├── features/                   # Feature documentation
│   ├── tutorials/                  # Tutorial guides
│   ├── api-reference/              # API documentation
│   ├── integrations/               # Integration guides
│   └── deployment/                 # Deployment guides
├── website/                        # Docusaurus configuration
│   ├── docusaurus.config.js        # Main configuration
│   ├── sidebars.js                 # Sidebar navigation
│   ├── package.json                # Dependencies
│   ├── src/                        # Custom components and styles
│   └── static/                     # Static assets
└── .github/
    └── workflows/
        └── deploy-docs.yml          # GitHub Actions workflow
```

## 🎨 Customization

### Updating Configuration
Edit `website/docusaurus.config.js` to customize:
- Site title and description
- URL and base URL for your deployment
- Navigation menu items
- Footer links
- Social media links

### Styling
Edit `website/src/css/custom.css` to customize the appearance.

### Adding New Documentation
1. Create new `.md` files in the `docs/` directory
2. Update `website/sidebars.js` to include them in navigation
3. Commit and push to trigger automatic deployment

## 🔧 Configuration Notes

### GitHub Repository Settings
Make sure your repository is configured correctly:

1. **Repository name**: Should match the `projectName` in `docusaurus.config.js`
2. **GitHub Pages**: Enable GitHub Pages with "GitHub Actions" as source
3. **Base URL**: Set to `/your-repository-name/` in the config file

### Environment Variables
You can set these in your GitHub repository secrets:
- `GOOGLE_ANALYTICS_ID`: For Google Analytics tracking
- `ALGOLIA_APP_ID`: For search functionality
- `ALGOLIA_API_KEY`: For search functionality

## 📞 Support

For documentation deployment issues:
- **Documentation**: docs@cryptomcp.dev
- **Technical Support**: support@cryptomcp.dev
- **GitHub Issues**: [Create an issue](https://github.com/cryptomcp/allinone-crypto-trading-mcp-server/issues)

---

**🎉 Your documentation is now ready for GitHub Pages deployment!**