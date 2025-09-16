"""
Telegram bot for crypto trading and monitoring.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from core.types import Exchange, Blockchain
from core.utils import format_currency
from cex.trading import execute_trade, get_balances
from cex.market_data import get_price_data
from addons.news.aggregator import get_news_feed, analyze_sentiment
from addons.signals.whales_tools import get_recent_whale_transactions
from addons.news.feargreed_tools import get_fear_greed_data
from env import config

logger = logging.getLogger(__name__)


class CryptoTradingBot:
    """Telegram bot for crypto trading and monitoring."""
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.admin_ids = [int(id) for id in config.TELEGRAM_ADMIN_IDS if id]
    
    def setup(self) -> None:
        """Set up the Telegram bot."""
        if not config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Register command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("balance", self.balance_command))
        self.app.add_handler(CommandHandler("price", self.price_command))
        self.app.add_handler(CommandHandler("trade", self.trade_command))
        self.app.add_handler(CommandHandler("news", self.news_command))
        self.app.add_handler(CommandHandler("whales", self.whales_command))
        self.app.add_handler(CommandHandler("fng", self.fear_greed_command))
        self.app.add_handler(CommandHandler("dex", self.dex_command))
        self.app.add_handler(CommandHandler("signals", self.signals_command))
        self.app.add_handler(CommandHandler("goat", self.goat_command))
        self.app.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.app.add_handler(CommandHandler("free_usdc", self.free_usdc_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        welcome_message = """
🚀 Welcome to All-in-One Crypto Trading Bot!

Available commands:
📊 /balance - View portfolio balances
💰 /price <symbol> - Get crypto prices
📈 /trade <symbol> <amount> <side> - Execute trades
📰 /news [symbol] - Latest crypto news
🐋 /whales - Recent whale transactions
😱 /fng - Fear & Greed Index
🔀 /dex <token> - DEX analytics
⚡ /signals - Trading signals
📊 /portfolio - Portfolio summary
🎯 /goat <command> - GOAT SDK operations
💸 /free_usdc <address> <amount> - Free USDC transfer
📊 /status - System status
❓ /help - Show this help message

Example: /price BTC
Example: /trade BTC/USDT 0.001 buy
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        await self.start_command(update, context)
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /balance command."""
        try:
            balances = await get_balances(include_zero=False)
            
            if not balances:
                await update.message.reply_text("No balances found.")
                return
            
            message = "💰 **Portfolio Balances:**\n\n"
            total_usd = 0
            
            for balance in balances[:20]:  # Limit to top 20
                if balance['total'] > 0:
                    # Simple USD estimation (would need price lookup)
                    message += f"• {balance['currency']}: {balance['total']:.6f}\n"
                    message += f"  Available: {balance['available']:.6f}\n"
                    if balance.get('exchange'):
                        message += f"  Exchange: {balance['exchange']}\n"
                    message += "\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching balances: {str(e)}")
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /price command."""
        try:
            if not context.args:
                await update.message.reply_text("Usage: /price <symbol>\nExample: /price BTC")
                return
            
            symbol = context.args[0].upper()
            price_data = await get_price_data(symbol)
            
            change_emoji = "📈" if price_data.get('change_24h_percent', 0) > 0 else "📉"
            
            message = f"""
{change_emoji} **{symbol} Price Update**

💰 Price: ${price_data['price']:,.2f}
📊 24h Change: {price_data.get('change_24h_percent', 0):.2f}%
📈 24h High: ${price_data.get('high_24h', 0):,.2f}
📉 24h Low: ${price_data.get('low_24h', 0):,.2f}
💹 24h Volume: ${price_data.get('volume_24h', 0):,.0f}

Source: {price_data.get('source', 'Unknown')}
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching price: {str(e)}")
    
    async def whales_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /whales command."""
        try:
            whale_transactions = await get_recent_whale_transactions(limit=10)
            
            if not whale_transactions:
                await update.message.reply_text("🐋 No recent whale transactions found.")
                return
            
            message = "🐋 **Recent Whale Transactions:**\n\n"
            
            for tx in whale_transactions[:5]:
                value_str = format_currency(tx.amount_usd, "USD")
                message += f"• {tx.token_symbol}: {value_str}\n"
                message += f"  Chain: {tx.blockchain.value}\n"
                message += f"  Type: {tx.transaction_type}\n"
                message += f"  Time: {tx.timestamp.strftime('%H:%M UTC')}\n\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching whale data: {str(e)}")
    
    async def fear_greed_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /fng command."""
        try:
            fng_data = await get_fear_greed_data()
            
            # Emotion based on value
            if fng_data['value'] <= 20:
                emoji = "😨"
            elif fng_data['value'] <= 40:
                emoji = "😟"
            elif fng_data['value'] <= 60:
                emoji = "😐"
            elif fng_data['value'] <= 80:
                emoji = "😊"
            else:
                emoji = "🤑"
            
            message = f"""
{emoji} **Fear & Greed Index**

📊 Current Score: {fng_data['value']}/100
📈 Classification: {fng_data['classification']}
🧠 Sentiment: {fng_data['sentiment']}

💡 {fng_data['description']}

🎯 Trading Tip: {fng_data['trading_suggestion']}
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching Fear & Greed Index: {str(e)}")
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /news command."""
        try:
            coins = None
            if context.args:
                coins = [arg.upper() for arg in context.args]
            
            news_items = await get_news_feed(coins=coins, limit=5)
            
            if not news_items:
                await update.message.reply_text("📰 No recent news found.")
                return
            
            message = "📰 **Latest Crypto News:**\n\n"
            
            for news in news_items:
                sentiment_emoji = {
                    'positive': '✅',
                    'negative': '❌',
                    'neutral': '➖',
                    'mixed': '🔄'
                }.get(news.sentiment.value, '➖')
                
                message += f"{sentiment_emoji} **{news.title[:100]}...**\n"
                message += f"Source: {news.source}\n"
                message += f"Time: {news.published_at.strftime('%H:%M UTC')}\n"
                if news.coins_mentioned:
                    message += f"Coins: {', '.join(news.coins_mentioned[:3])}\n"
                message += "\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching news: {str(e)}")
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /portfolio command."""
        try:
            from portfolio.manager import get_portfolio_summary, get_asset_allocation
            
            portfolio = await get_portfolio_summary()
            allocation = await get_asset_allocation()
            
            message = f"📊 **Portfolio Summary**\n\n"
            message += f"💰 Total Value: ${portfolio.total_value_usd:,.2f}\n"
            message += f"📈 Daily P&L: ${portfolio.daily_pnl:,.2f}\n"
            message += f"📉 Unrealized P&L: ${portfolio.unrealized_pnl:,.2f}\n\n"
            
            message += "**Top Holdings:**\n"
            top_holdings = list(allocation['top_holdings'].items())[:5]
            for symbol, data in top_holdings:
                percentage = data['percentage']
                value = data['value_usd']
                message += f"• {symbol}: ${value:,.2f} ({percentage:.1f}%)\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching portfolio: {str(e)}")
    
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /signals command."""
        try:
            from ai.signals import get_latest_signals
            
            signals = await get_latest_signals(limit=5)
            
            if not signals:
                await update.message.reply_text("⚡ No trading signals available.")
                return
            
            message = "⚡ **Latest Trading Signals:**\n\n"
            
            for signal in signals:
                signal_emoji = {
                    'buy': '🟢',
                    'sell': '🔴',
                    'hold': '🟡',
                    'strong_buy': '🟢🟢',
                    'strong_sell': '🔴🔴'
                }.get(signal.signal_type.value, '⚫')
                
                message += f"{signal_emoji} **{signal.symbol}** - {signal.signal_type.value.upper()}\n"
                message += f"Confidence: {signal.confidence*100:.1f}%\n"
                if signal.price_target:
                    message += f"Target: ${signal.price_target:.2f}\n"
                message += f"Reason: {signal.reasoning[:100]}...\n\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error fetching signals: {str(e)}")
    
    async def goat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /goat command."""
        try:
            if not context.args:
                await update.message.reply_text("Usage: /goat <command> [params]\nExample: /goat status")
                return
            
            command = context.args[0].lower()
            
            if command == "status":
                from addons.goat.goat_proxy import get_goat_status
                
                status = await get_goat_status()
                
                message = f"🎯 **GOAT SDK Status**\n\n"
                message += f"Enabled: {'✅' if status.get('enabled') else '❌'}\n"
                message += f"Available: {'✅' if status.get('available') else '❌'}\n"
                
                if status.get('version'):
                    message += f"Version: {status['version']}\n"
                
                if status.get('supported_chains'):
                    chains = ', '.join(status['supported_chains'])
                    message += f"Chains: {chains}\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            
            else:
                await update.message.reply_text(f"Unknown GOAT command: {command}")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error executing GOAT command: {str(e)}")
    
    async def free_usdc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /free_usdc command."""
        try:
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /free_usdc <address> <amount>\nExample: /free_usdc 0x123... 100")
                return
            
            to_address = context.args[0]
            amount = Decimal(context.args[1])
            
            from addons.base_free.base_free_usdc import check_transfer_eligibility, transfer_free_usdc
            
            # Check eligibility first
            eligibility = await check_transfer_eligibility(to_address, amount)
            
            if not eligibility['eligible']:
                await update.message.reply_text(f"❌ Transfer not eligible: {eligibility['reason']}")
                return
            
            # Execute transfer (dry run for now)
            result = await transfer_free_usdc(to_address, amount, dry_run=True)
            
            if result['success']:
                message = f"💸 **Free USDC Transfer Simulation**\n\n"
                message += f"Amount: {amount} USDC\n"
                message += f"Recipient: {to_address[:10]}...\n"
                message += f"Network: Base\n"
                message += f"Gas Savings: ~$0.50\n"
                message += f"\n✅ Transfer eligible and ready!"
            else:
                message = f"❌ Transfer failed: {result.get('message', 'Unknown error')}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error with free USDC transfer: {str(e)}")
    
    def run(self) -> None:
        """Run the Telegram bot."""
        if not self.app:
            self.setup()
        
        logger.info("Starting Telegram bot...")
        self.app.run_polling()


if __name__ == "__main__":
    bot = CryptoTradingBot()
    bot.run()