#!/usr/bin/python
"""
App for testing out trading ideas
"""

import datetime
import sys
import os
import glob
import math
import pygame
from pygame.locals import *
from enums import TradeMode, TradeType, TradeState, Stats, OHLC


CHARTTOPYOFFSET = 150
CHARTRIGHTSPACING = 60
TRADERISKPERCENT = 0.01
TRADERISKPIPS = 80
    
def draw_horizontal_dashed_line(surf, colour, start_pos, end_pos, width=1, dash_length=10):
    length = end_pos[0] - start_pos[0]
    y_value = start_pos[1]
    for index in range(0, length//dash_length, 2):
        start = start_pos[0] + (index    * dash_length)
        end   = start_pos[0] + ((index + 1) * dash_length)
        pygame.draw.line(surf, colour, (start, y_value), (end, y_value), width)

class Trading():
    """
    Trading Practice App
    """
    def __init__(self):
        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        self.settings_dir = 'settings'
        if not os.path.exists(self.settings_dir):
            os.mkdir(self.settings_dir)
        self.config_file = os.path.join(self.settings_dir, 'config.txt')
        self.fade_file = os.path.join(self.settings_dir, 'fade.txt')
        self.trend_file = os.path.join(self.settings_dir, 'trend.txt')
        self.history_file = os.path.join(self.settings_dir, 'history.txt')
        self.done = False
        self.bull_candle_colour = (20, 255, 20)
        self.bear_candle_colour = (255, 20, 20)
        self.doji_candle_colour = (125, 125, 125)
        self.order_colour = (20, 255, 20)
        self.stop_loss_colour = (255, 20, 20)
        self.max_candles = 450
        self.last_candle = self.max_candles
        self.candle_width = 3
        self.candle_spacing = 1
        self.chart_pip_height = 800
        self.load_data()
        pygame.init()
        self.screen = pygame.display.set_mode(size=(1920, 1080), flags=pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE, depth=32, display=0)
        pygame.display.set_caption("Trading Practice App")
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 20)
        self.price_level_font = pygame.font.SysFont('Comic Sans MS', 15)
        self.start_time = datetime.datetime.now()
        self.screen_width, self.screen_height = pygame.display.get_surface().get_size()
        self.first_run = True
        self.showing_help = False
        self.trade_state = TradeState()
        self.stats = Stats()
        self.history = list()
        self.show_history = True
        self.readConfig()

    def load_data(self):
        """
        Reads the data from the files
        """
        def get_filename(file_list, file_search):
            for filename in file_list:
                if file_search in filename.lower():
                    return filename

        filenames = glob.glob(os.path.join('.', self.data_dir, "*"))
        if len(filenames) > 0:
            hourly_file = get_filename(filenames, 'hourly')
            four_hourly_file = get_filename(filenames, '4 hours')
            daily_file = get_filename(filenames, 'daily')
            with open(hourly_file) as ask_file:
                self.ask = ask_file.readlines()
            tick_file = get_filename(filenames, 'tick')
            # if tick_file:
            #     with open(tick_file) as tick_data:
            #         self.tick = tick_data.readlines()
            # print('loaded')
        self.bid = self.ask

    def draw_chart(self):
        """
        Draws the chart
        """
        if self.last_candle < self.max_candles:
            self.last_candle = self.max_candles
        maxheight = 0
        minheight = 9999
        for x in range(0, self.max_candles):
            offset = self.last_candle-x
            high = float(self.bid[offset].split(',')[OHLC.HIGHINDEX.value])
            if high > maxheight:
                maxheight = high
            low = float(self.bid[offset].split(',')[OHLC.LOWINDEX.value])
            if low < minheight:
                minheight = low
        factor = (self.screen_height - CHARTTOPYOFFSET) / self.chart_pip_height * 10000
        #Draw Price Lines
        for x in range(0, self.chart_pip_height, 20):
            val = float("%.3f" % maxheight) - x*0.0001
            line_ypos = int(self.screen_height - (val-minheight) * factor) - CHARTTOPYOFFSET
            pygame.draw.line(self.screen, self.doji_candle_colour, (0, line_ypos), (self.screen_width - CHARTRIGHTSPACING - 5, line_ypos), 1)
            text = self.price_level_font.render(str(val).ljust(7, '0'), 1, (self.bear_candle_colour))
            self.screen.blit(text, (self.screen_width - CHARTRIGHTSPACING, line_ypos - 13))
        #Draw Chart Data
        for x in range(0, self.max_candles):
            offset = self.last_candle-x
            xpos = self.candle_spacing + (self.candle_spacing + self.candle_width) * (self.max_candles-x)
            open_price = float(self.bid[offset].split(',')[OHLC.OPENINDEX.value])
            high_price = float(self.bid[offset].split(',')[OHLC.HIGHINDEX.value])
            low_price = float(self.bid[offset].split(',')[OHLC.LOWINDEX.value])
            close_price = float(self.bid[offset].split(',')[OHLC.CLOSEINDEX.value])
            candle_open_ypos = int(self.screen_height - (open_price-minheight) * factor) - CHARTTOPYOFFSET
            candle_high_ypos = int(self.screen_height - (high_price-minheight) * factor) - CHARTTOPYOFFSET
            candle_low_ypos = int(self.screen_height - (low_price-minheight) * factor) - CHARTTOPYOFFSET
            candle_close_ypos = int(self.screen_height - (close_price-minheight) * factor) - CHARTTOPYOFFSET
            candle_close_distance = int(abs(open_price-close_price) * factor)
            if candle_open_ypos < candle_close_ypos:
                pygame.draw.rect(self.screen, self.bear_candle_colour, (xpos, candle_open_ypos, self.candle_width, candle_close_distance))
                #Draw Candle Wick
                pygame.draw.line(self.screen, self.doji_candle_colour, (xpos+int(self.candle_width/2), candle_high_ypos), (xpos+int(self.candle_width/2), candle_open_ypos), 1)
                pygame.draw.line(self.screen, self.doji_candle_colour, (xpos+int(self.candle_width/2), candle_low_ypos), (xpos+int(self.candle_width/2), candle_close_ypos), 1)
            elif candle_open_ypos > candle_close_ypos:
                pygame.draw.rect(self.screen, self.bull_candle_colour, (xpos, candle_close_ypos, self.candle_width, candle_close_distance))
                #Draw Candle Wick
                pygame.draw.line(self.screen, self.doji_candle_colour, (xpos+int(self.candle_width/2), candle_high_ypos), (xpos+int(self.candle_width/2), candle_close_ypos), 1)
                pygame.draw.line(self.screen, self.doji_candle_colour, (xpos+int(self.candle_width/2), candle_low_ypos), (xpos+int(self.candle_width/2), candle_open_ypos), 1)
            #Draw Candle Body
            pygame.draw.line(self.screen, self.doji_candle_colour, (xpos, candle_open_ypos), (xpos+self.candle_width, candle_open_ypos), 1)
            pygame.draw.line(self.screen, self.doji_candle_colour, (xpos+self.candle_width, candle_open_ypos), (xpos+self.candle_width, candle_close_ypos), 1)
            pygame.draw.line(self.screen, self.doji_candle_colour, (xpos, candle_close_ypos), (xpos+self.candle_width, candle_close_ypos), 1)
            pygame.draw.line(self.screen, self.doji_candle_colour, (xpos, candle_open_ypos), (xpos, candle_close_ypos), 1)
        #Draw open position and stop loss
        if (self.trade_state.trade_mode != TradeMode.CLOSED):
            order_ypos = int(self.screen_height - (self.trade_state.order_price-minheight) * factor) - CHARTTOPYOFFSET
            stop_ypos = int(self.screen_height - (self.trade_state.stop_loss_price-minheight) * factor) - CHARTTOPYOFFSET
            draw_horizontal_dashed_line(self.screen, self.order_colour, (0, order_ypos), (self.screen_width - CHARTRIGHTSPACING, order_ypos))
            draw_horizontal_dashed_line(self.screen, self.stop_loss_colour, (0, stop_ypos), (self.screen_width - CHARTRIGHTSPACING, stop_ypos))
        #Draw historical trades
        if self.show_history:
            history_offset = self.last_candle - self.max_candles
            for hist in self.history:
                if int(hist[2]) >= history_offset and int(hist[2]) <= self.last_candle:
                    history_open_xpos = self.candle_spacing + (self.candle_spacing + self.candle_width) * (self.max_candles - (self.last_candle - int(hist[0])))
                    history_open_trade_ypos = int(self.screen_height - (float(hist[1])-minheight) * factor) - CHARTTOPYOFFSET
                    history_close_xpos = self.candle_spacing + (self.candle_spacing + self.candle_width) * (self.max_candles - (self.last_candle - int(hist[2])))
                    history_close_trade_ypos = int(self.screen_height - (float(hist[3])-minheight) * factor) - CHARTTOPYOFFSET
                    history_colour = self.bull_candle_colour if int(hist[4]) == TradeMode.BUY.value else self.bear_candle_colour
                    pygame.draw.line(self.screen, history_colour, (history_open_xpos, history_open_trade_ypos), (history_close_xpos, history_close_trade_ypos), 1)

    def main_loop(self):
        """
        The loop that runs the app
        """
        try:
            while not self.done:
                self.do_events()
                self.screen.fill((45, 45, 45))
                self.check_orders()
                self.draw_info_text()
                if self.showing_help:
                    self.displayHelp()
                self.draw_chart()
                pygame.display.flip()
                self.first_run = False
        except:
            print("Unexpected error:", sys.exc_info())

    def check_orders(self):
        if (self.trade_state.trade_mode == TradeMode.BUY):
            self.trade_state.pips = 1 + (float(self.bid[self.last_candle].split(',')[OHLC.CLOSEINDEX.value]) - self.trade_state.order_price) * 10000
            self.trade_state.profit = self.trade_state.pips * self.trade_state.position_size * 100
            if float(self.bid[self.last_candle].split(',')[OHLC.LOWINDEX.value]) <= self.trade_state.stop_loss_price:
                self.close(self.trade_state.trade_type, self.trade_state.stop_loss_price)

        if (self.trade_state.trade_mode == TradeMode.SELL):
            self.trade_state.pips = 1 + (self.trade_state.order_price - float(self.ask[self.last_candle].split(',')[OHLC.CLOSEINDEX.value])) * 10000 
            self.trade_state.profit = self.trade_state.pips * self.trade_state.position_size * 100
            if float(self.ask[self.last_candle].split(',')[OHLC.HIGHINDEX.value]) >= self.trade_state.stop_loss_price:
                self.close(self.trade_state.trade_type, self.trade_state.stop_loss_price)

    def draw_info_text(self):
        last_candle_data_text = self.font.render(self.bid[self.last_candle], 1, (self.bear_candle_colour))
        self.screen.blit(last_candle_data_text, (20, 20))
        equity_text = self.font.render("Pre-Trade Balance: " + str("%.2f" % (self.trade_state.equity)), 1, (self.bear_candle_colour))
        self.screen.blit(equity_text, (20, 45))
        equity_text = self.font.render("Equity: " + str("%.2f" % (self.trade_state.equity + self.trade_state.profit)), 1, (self.bear_candle_colour))
        self.screen.blit(equity_text, (20, 70))
        profit_text = self.font.render("Profit: " + str("%.2f" % self.trade_state.profit), 1, (self.bear_candle_colour))
        self.screen.blit(profit_text, (20, 95))
        trade_mode_text = self.font.render("Trade Mode: " + str(self.trade_state.trade_mode.name), 1, (self.bear_candle_colour))
        self.screen.blit(trade_mode_text, (20, 120))
        pips_text = self.font.render("Pips: " + str("%.1f" % self.trade_state.pips), 1, (self.bear_candle_colour))
        self.screen.blit(pips_text, (20, 145))
        position_size_text = self.font.render("Position Size: " + str("%.4f" % self.trade_state.position_size), 1, (self.bear_candle_colour))
        self.screen.blit(position_size_text, (20, 170))
        help_text = self.font.render("Press F1 to toggle help info ", 1, (self.bear_candle_colour))
        self.screen.blit(help_text, (20, 195))

    def buy(self, trade_type):
        if self.trade_state.trade_mode == TradeMode.CLOSED:
            self.trade_state.trade_mode = TradeMode.BUY
            self.trade_state.order_price = float(self.ask[self.last_candle].split(',')[OHLC.CLOSEINDEX.value])
            self.trade_state.stop_loss_price = self.trade_state.order_price - TRADERISKPIPS * 0.0001
            self.trade_state.position_size = self.trade_state.equity * TRADERISKPERCENT / TRADERISKPIPS * 0.01
            self.trade_state.candle_number = self.last_candle
            self.trade_state.trade_type = trade_type

    def sell(self, trade_type):
        if self.trade_state.trade_mode == TradeMode.CLOSED:
            self.trade_state.trade_mode = TradeMode.SELL
            self.trade_state.order_price = float(self.bid[self.last_candle].split(',')[OHLC.CLOSEINDEX.value])
            self.trade_state.stop_loss_price = self.trade_state.order_price + TRADERISKPIPS * 0.0001
            self.trade_state.position_size = self.trade_state.equity * TRADERISKPERCENT / TRADERISKPIPS * 0.01
            self.trade_state.candle_number = self.last_candle
            self.trade_state.trade_type = trade_type

    def close(self, trade_type, close_price=None):
        if self.trade_state.trade_mode != TradeMode.CLOSED:
            self.history.append([
                self.trade_state.candle_number,
                self.trade_state.order_price,
                self.last_candle,
                close_price or self.ask[self.last_candle].split(',')[OHLC.CLOSEINDEX.value],
                self.trade_state.trade_mode.value
            ])
            self.trade_state.trade_mode = TradeMode.CLOSED
            self.trade_state.equity += self.trade_state.profit
            if trade_type == TradeType.FADE:
                self.stats.fade.append(self.trade_state.pips)
            else:
                self.stats.trend.append(self.trade_state.pips)
            self.trade_state.profit = 0
            self.trade_state.order_price = 0
            self.trade_state.position_size = 0
            self.trade_state.stop_loss_price = 0
            self.trade_state.pips = 0

    def do_events(self):
        """
        Query for quit and keypress events
        """
        events = pygame.event.get(pump=True)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.writeConfig()
                    self.done = True
                if event.key == pygame.K_UP:
                    self.chart_pip_height+=20
                if event.key == pygame.K_DOWN:
                    self.chart_pip_height-=20
                if event.key == pygame.K_LEFT:
                    self.last_candle -= 1
                    if self.last_candle < self.max_candles:
                        self.last_candle = self.max_candles
                if event.key == pygame.K_RIGHT:
                    self.last_candle += 1
                if event.key == pygame.K_PAGEDOWN:
                    self.last_candle -= 5
                    if self.last_candle < self.max_candles:
                        self.last_candle = self.max_candles
                if event.key == pygame.K_PAGEUP:
                    self.last_candle += 5
                if event.key == pygame.K_h:
                    self.show_history = not self.show_history
                if event.key == pygame.K_b:
                    self.buy(TradeType.FADE)
                if event.key == pygame.K_n:
                    self.buy(TradeType.TREND)
                if event.key == pygame.K_s:
                    self.sell(TradeType.FADE)
                if event.key == pygame.K_d:
                    self.sell(TradeType.TREND)
                if event.key == pygame.K_c:
                    self.close(self.trade_state.trade_type)
                if event.key == pygame.K_F1:
                    self.showing_help = not self.showing_help
                if event.key == pygame.K_1:
                    self.max_candles = 450
                    self.candle_width = 3
                    self.candle_spacing = 1
                if event.key == pygame.K_2:
                    self.max_candles = 600
                    self.candle_width = 2 
                    self.candle_spacing = 1
                if event.key == pygame.K_3:
                    self.max_candles = 900
                    self.candle_width = 1
                    self.candle_spacing = 1
                if event.key == pygame.K_4:
                    self.max_candles = 1800
                    self.candle_width = 1
                    self.candle_spacing = 0
            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                rel = pygame.mouse.get_rel()[0]
                move=0
                if rel > 0:
                    move = -15
                elif rel < 0:
                    move = +15 
                self.last_candle += move
            if event.type is QUIT:
                self.writeConfig()
                self.done = True

    def displayHelp(self):
        text1 = "Move 1 candle: use left and right arrow."
        text2 = "Move multiple candles: use PageUp and PageDown."
        text3 = "Buy/Sell. Tracked as Fade Trade: b/s."
        text4 = "Buy/Sell. Tracked as Trend Trade: n/d."
        text5 = "Change Zoom: 1-4."
        text6 = "Exit: Escape."
        text1_text = self.font.render(text1, 1, (self.bear_candle_colour))
        text2_text = self.font.render(text2, 1, (self.bear_candle_colour))
        text3_text = self.font.render(text3, 1, (self.bear_candle_colour))
        text4_text = self.font.render(text4, 1, (self.bear_candle_colour))
        text5_text = self.font.render(text5, 1, (self.bear_candle_colour))
        text6_text = self.font.render(text6, 1, (self.bear_candle_colour))
        self.screen.blit(text1_text, (700, 60))
        self.screen.blit(text2_text, (700, 85))
        self.screen.blit(text3_text, (700, 110))
        self.screen.blit(text4_text, (700, 135))
        self.screen.blit(text5_text, (700, 160))
        self.screen.blit(text6_text, (700, 185))
    
    def readConfig(self):
        if os.path.exists(self.config_file):
            with open(self.config_file) as config_file:
                data = config_file.readlines()
                if len(data) == 2:
                    self.trade_state.equity = float(data[0].rstrip())
                    self.last_candle = int(data[1].rstrip())
            if os.path.exists(self.fade_file):
                with open(self.fade_file) as config_file:
                    data = config_file.readlines()
                    for x in data:
                        x = x.rstrip()
                        if x != "":
                            self.stats.fade.append(x)
            if os.path.exists(self.trend_file):
                with open(self.trend_file) as config_file:
                    data = config_file.readlines()
                    for x in data:
                        x = x.rstrip()
                        if x != "":
                            self.stats.trend.append(x)
            if os.path.exists(self.history_file):
                with open(self.history_file) as config_file:
                    data = config_file.readlines()
                    self.history = list(x.rstrip().split() for x in data if x != "")

    def writeConfig(self):
        with open(self.config_file, "w") as config_file:
            config_file.write(str(self.trade_state.equity)+"\n")
            config_file.write(str(self.last_candle)+"\n")
        with open(self.fade_file, "w") as fade_file:
            for x in self.stats.fade:
                fade_file.write(str("%.1f" % float(x))+"\n")
        with open(self.trend_file, "w") as trend_file:
            for x in self.stats.trend:
                trend_file.write(str("%.1f" % float(x))+"\n")
        with open(self.history_file, "w") as history_file:
            for x in self.history:
                history_file.write("{0} {1} {2} {3} {4}\n".format(x[0], x[1], x[2], x[3], x[4]))


if __name__ == "__main__":
    app = Trading()
    app.main_loop()
