from datetime import datetime, timedelta
from sqlalchemy import DECIMAL, Interval
from sqlalchemy.dialects.mysql import DECIMAL
from tradepilot import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_data = db.relationship('UserData', backref='owner', lazy=True)

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    min_trading_days = db.Column(db.String(255))
    max_daily_loss = db.Column(db.String(255))
    max_loss = db.Column(db.String(255))
    profit_target = db.Column(db.String(255))
    instrument = db.Column(db.String(255))
    trading_session = db.Column(db.String(255))
    risk_reward = db.Column(db.String(255))
    daily_max_loss = db.Column(db.String(255))
    consecutive_losers = db.Column(db.String(255))
    trading_strategy = db.Column(db.String(255))
    timeframes = db.Column(db.String(255))
    trades_per_day = db.Column(db.String(255))

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket = db.Column(db.String(20), nullable=False)
    open_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    trade_type = db.Column(db.String(10), nullable=False)
    size = db.Column(db.Float, nullable=False)
    item = db.Column(db.String(20), nullable=False)
    price = db.Column(DECIMAL(10, 2), nullable=False)
    s_l = db.Column(DECIMAL(10, 2), nullable=False)
    t_p = db.Column(DECIMAL(10, 2), nullable=False)
    close_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    close_price = db.Column(DECIMAL(10, 2), nullable=False)
    comm = db.Column(DECIMAL(10, 2), nullable=False)
    taxes = db.Column(DECIMAL(10, 2), nullable=False)
    swap = db.Column(DECIMAL(10, 2), nullable=False)
    profit = db.Column(DECIMAL(10, 2), nullable=False)
    pips = db.Column(DECIMAL(10, 2), nullable=True)
    duration = db.Column(db.Interval, nullable=True)

    def calculate_pips(self):
        if self.trade_type.lower() == 'buy':
            self.pips = self.close_price - self.price
        else:
            self.pips = self.price - self.close_price

    def calculate_duration(self):
        self.duration = self.close_time - self.open_time

    @staticmethod
    def create_trade(data):
        trade = Trade(
            user_id=data['user_id'],
            ticket=data['ticket'],
            open_time=data['open_time'],
            close_time=data['close_time'],
            trade_type=data['trade_type'],
            size=data['size'],
            item=data['item'],
            price=data['price'],
            s_l=data['s_l'],
            t_p=data['t_p'],
            close_price=data['close_price'],
            comm=data['comm'],
            taxes=data['taxes'],
            swap=data['swap'],
            profit=data['profit']
        )
        trade.calculate_pips()
        trade.calculate_duration()
        return trade