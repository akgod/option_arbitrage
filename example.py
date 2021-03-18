import okex.account_api as account
import okex.futures_api as future
import okex.lever_api as lever
import okex.spot_api as spot
import okex.swap_api as swap
import okex.index_api as index
import okex.option_api as option
import json
import logging
import datetime
import time
from threading import Thread

OptionTime = '200807'                                                                                                          # 合约行权日期，获取同一行权日所有期权合约的参数
Profit_Sum = 0.0
Times_Sum = 0
badTimes = 0
Par_ProfitMin = 50                                                                                                                # 平价套利空间触发值。单位美元
PriceDiscount_ProfitMin = 10                                                                                                      #价格贴现套利，空间触发值
Write_p = 0                                                                                                                       # 套利空间大于该值，写入文件，便于统计分析
s = 2                                                                                                                          # 每次最大下单量，自定义
v =1                                                                                                                            #下单量
lever_future = 3                                                                                                                #期货的杠杆倍数
margin_Safe = 1.7                                                                                                               #账户可用余额应是最低维持保证金的倍数，以防止减仓行为
FutureSubject = 'BTC-USDT-' + OptionTime                                                                                               # 期货合约标的名称，当周
order_protect = 6                                                                                                              #为了保证下单大概率立刻成交，下单保护值。卖减该值，买加该值

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='mylog-rest.json', filemode='a', format=log_format, level=logging.INFO)
# logging.warning('warn message')
# logging.info('info message')
# logging.debug('debug message')
# logging.error('error message')
# logging.critical('critical message')

def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"

def min(x, y, z,t):
    min = x
    if y <min:
        min = y
    if z < min:
        min = z
    if t < min:
        min = t
    return (min)
def max(a,b):
    max = a
    if b >a:
        max = b
    return max

def safeProtect():                      # 获取等待期权合约和期货合约未成交订单的数量的最大值
    q = 1
    while q:
        try:
            orders_Option = optionAPI.get_order_list('BTC-USD', '0')
            orders_Future = futureAPI.get_order_list(FutureSubject, '0')
            q = 0
            if len(orders_Option) > len(orders_Future):
                return len(orders_Option)
            else:
                return len(orders_Future)
        except:
            print("@@@@@@读取订单列表失败@@@@@@")
            time.sleep(0.2)
            continue

def get_data(i):
    if i == 1:
        result = futureAPI.get_depth(FutureSubject)                                 # 获取期货合约深度数据dict￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥
    if i == 2:
        result = futureAPI.get_specific_ticker(FutureSubject)                       # 获取期货合约买一卖一价格dict￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥
    if i == 3:
        result = optionAPI.get_instruments_summary('BTC-USD',delivery=OptionTime)  # 获取同一行权日期OptionTime所有期权合约定价详情list￥￥￥￥￥￥￥￥￥
    if i == 4:
        result = optionAPI.get_underlying_account('BTC-USD')                       # 期权合约的账户信息
    if i == 5:
        result = futureAPI.get_coin_account('BTC-USDT')                              # 交割合约的btc-usdt账户信息
    if i == 6:
        result = futureAPI.get_mark_price(FutureSubject)                            # 获取交割合约标记价格信息
    if i == 7:
        result = indexAPI.get_index_constituents('BTC-USD')                         # 获取现货美元指数信息 BTC-USD
    if i == 8:
        result = indexAPI.get_index_constituents('BTC-USDT')                         # 获取现货usdt指数信息 BTC-USDT
    return result

class MyThread(Thread):
    def __init__(self, i):
        Thread.__init__(self)
        self.i = i
    def run(self):
        self.data = get_data(self.i)
    def get_result(self):
        return self.data

if __name__ == '__main__':
    api_key = "********************"
    seceret_key = "*****************"
    passphrase = "tothemoon"
    futureAPI = future.FutureAPI(api_key, seceret_key, passphrase, True)  # future api test
    optionAPI = option.OptionAPI(api_key, seceret_key, passphrase,True)  # option api test
    indexAPI = index.IndexAPI(api_key, seceret_key, passphrase, True)    # index api test

    strike_result = optionAPI.get_instruments('BTC-USD', delivery=OptionTime)
    #print('strike=', str(strike_result))
    #print('typeis',type(strike_result))
    ExercisePrice = []                                       # 期权合约行权价格list
    for i in range(len(strike_result)):
        strike = strike_result[i]['strike']
        #print('-------',strike)
        #print('########',type(strike))
        if ExercisePrice.count(strike) == 0:                 #统计ExercisePrice list中，strike的出现次数。若为0，添加进去
            ExercisePrice.append(strike)
    print('@@@@@@@@@@@',ExercisePrice)

    while 1:
        if safeProtect() > 4:                                                           #未成交订单数量太多，保护机制
            print("@@@@@有好多订单未成交@@@@@@",str(safeProtect()))
            time.sleep(0.6)
            continue
        timeNow = get_timestamp()
        future_size = {}
        future_price = {}
        result = []
        accountInfo_Option = {}
        accountInfo_future = {}
        markpriceInfo_future = {}
        indexInfo_btcusd = {}
        indexInfo_btcusdt = {}
        try:
            td1 = MyThread(1)
            td2 = MyThread(2)
            td3 = MyThread(3)
            td4 = MyThread(4)
            td5 = MyThread(5)
            td6 = MyThread(6)
            td7 = MyThread(7)
            td8 = MyThread(8)
            td1.start()
            td2.start()
            td3.start()
            td4.start()
            td5.start()
            td6.start()
            td7.start()
            td8.start()
            td1.join()
            td2.join()
            td3.join()
            td4.join()
            td5.join()
            td6.join()
            td7.join()
            td8.join()
            future_size = td1.get_result()                                              # 获取期货合约深度数据dict￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥
            future_price = td2.get_result()                                             # 获取期货合约买一卖一价格dict￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥
            result = td3.get_result()                                                   # 获取同一行权日期OptionTime所有期权合约定价详情list￥￥￥￥￥￥￥￥￥
            accountInfo_Option = td4.get_result()                                       # 期权合约的账户信息
            accountInfo_future = td5.get_result()                                       # 交割合约的btc账户信息
            markpriceInfo_future = td6.get_result()                                     # 获取交割合约标记价格信息
            indexInfo_btcusd = td7.get_result()                                         # 获取现货美元指数信息 BTC-USD
            indexInfo_btcusdt = td8.get_result()                                        # 获取现货usdt指数信息 BTC-USDT
        except:
            print(timeNow,"@@@@@@@数据获取异常@@@@@")
            badTimes += 1
            continue

        # print( "future_size=",future_size)
        # print( "future_price=",future_price)
        # print("result=",result)
        # print("accountInfo_Option=",accountInfo_Option)
        # print("accountInfo_future=",accountInfo_future)
        # print("markpriceInfo_future=",markpriceInfo_future)
        # print("indexInfo_btcusd=",indexInfo_btcusd)

        total_avail_balance_Option = float(accountInfo_Option['total_avail_balance'])
        maintenance_margin = accountInfo_Option['maintenance_margin']
        if float(total_avail_balance_Option) < margin_Safe * float(maintenance_margin):  # 账户可用余额若小于 安全系数*当前最低维持保证金。退出本次套利
            print(timeNow, "@@@@@@@账户风险度太高@@@@@")
            time.sleep(2)
            continue
        total_avail_balance_Future = float(accountInfo_future['total_avail_balance'])         #交割合约可用余额

        a_Future = float(future_price['best_ask'])                                    # 得到期货合约买一卖一价格，最新成交价格
        b_Future = float(future_price['best_bid'])
        last_Future = float(future_price['last'])
        index_Future = round((a_Future + b_Future + last_Future)/3, 2)                 #求得期货合约价格指数。买一卖一价格，最新成交价格。三者的均值。作为期货标的指数
        # s3_asks = int(future_size['asks'][0][1])                                      # 得到期货合约买一卖一盘口数量
        # s3_bids = int(future_size['bids'][0][1])
        mark_price_future = float(markpriceInfo_future['mark_price'])                 # 得到交割合约标记价格
        index_btcusd = float(indexInfo_btcusd['data']['last'])                        # 得到btcusd价格指数
        index_btcusdt = float(indexInfo_btcusdt['data']['last'])                      # 得到btcusdt价格指数

        for index_EP in range(len(ExercisePrice)):
            OptionSubject_C = 'BTC-USD-' + OptionTime + '-' + ExercisePrice[index_EP] + '-C'  # 期权合约标的instrument_id，当周看涨
            OptionSubject_P = 'BTC-USD-' + OptionTime + '-' + ExercisePrice[index_EP] + '-P'  # 期权合约标的instrument_id，当周看跌
            exerciseprice_float = float(ExercisePrice[index_EP])                              # 期权执行价格
            for i in range(len(result)):
                if OptionSubject_C == result[i]['instrument_id']:
                    a_C = result[i]['best_ask']                                                             # 获取看涨期权卖一价格
                    b_C = result[i]['best_bid']                                                             # 获取看涨期权买一价格
                    mark_price_C = result[i]['mark_price']                                                  # 获取看涨期权标记价格
                    for j in range(len(result)):
                        if OptionSubject_P == result[j]['instrument_id']:
                            a_P = result[j]['best_ask']                                                     # 获取看跌期权卖一价格
                            b_P = result[j]['best_bid']                                                     # 获取看跌期权买一价格
                            mark_price_P = result[j]['mark_price']                                          # 获取看跌期权标记价格
                            if index_Future >= exerciseprice_float:                                         # 看涨期权为实值
                                    try:
                                        t1_a = float(a_C) * index_Future - (index_Future - exerciseprice_float)  # 计算看涨期权的时间价值
                                        t1_b = float(b_C) * index_Future - (index_Future - exerciseprice_float)
                                        t2_a = float(a_P) * index_Future                                         # 计算看跌期权的时间价值
                                        t2_b = float(b_P) * index_Future
                                    except:
                                        print(timeNow,OptionSubject_C,"或",OptionSubject_P,"！！！！----买一卖一价格或盘口深度为空-----")
                                        time.sleep(0.3)
                                        continue

                                    if t1_a < 0:                                                              # 价格贴现套利,买入看涨期权,期货做空
                                        p = abs(t1_a)                                                         # 计算标的套利空间
                                        if p > Write_p:
                                            textName = OptionTime + 'PriceDiscount.txt'
                                            f = open(textName, 'a')
                                            f.write('\n' + str(p))
                                            f.close()
                                        if p > PriceDiscount_ProfitMin:
                                                if 1000 * v > 10000 * b_Future:                          # 期权每次下单量为v,期货需做空 1000*v，需做多10000*b_Future。最终下单量为v_F.单位：张。
                                                    v_F = 1000 * v - 10000 * b_Future
                                                if 1000 * v < 10000 * b_Future:
                                                    v_F = 10000 * b_Future - 1000 * v

                                                btcNeed_Future = v_F*index_btcusdt/lever_future                          #交割合约下单所需保证金
                                                if total_avail_balance_Future < 1.02 * btcNeed_Future:
                                                    print(timeNow, "@@@@@@@@@@@交割合约账户余额不足@@@@@@@@@@")
                                                    time.sleep(0.3)
                                                    continue

                                                btcNeed_Option = float(a_C)*0.1*v                                         #期权合约下单所需保证金
                                                if total_avail_balance_Option < 1.01 * btcNeed_Option:
                                                    print(timeNow, "@@@@@@@@@@@期权合约账户余额不足@@@@@@@@@@")
                                                    time.sleep(0.3)
                                                    continue

                                                print(timeNow,"￥￥￥￥￥---价格贴现套利咯-------下单-----￥￥￥￥￥---")

                                                try:
                                                    order_option = optionAPI.take_order(instrument_id = OptionSubject_C,side= 'buy', order_type= '0', price= a_C, size= v,match_price= '0')
                                                    if 1000*v > 10000*b_Future:
                                                        order_future = futureAPI.take_order(FutureSubject, '2', b_Future - order_protect, v_F, match_price='0')
                                                    if 1000*v < 10000*b_Future:
                                                        order_future = futureAPI.take_order(FutureSubject, '1', a_Future + order_protect, v_F, match_price='0')

                                                except:
                                                    print(timeNow,"@@@@@@@@@@@下单失败@@@@@@@@@@")
                                                    time.sleep(0.3)
                                                    continue
                                                Profit_Sum += p*v*0.1
                                                Times_Sum += 1

                                                textName_order = OptionTime + 'Orders.txt'                                          #下单信息写入文件
                                                f = open(textName_order, 'a')
                                                f.write('\n' + timeNow + '￥￥￥￥￥￥￥￥￥￥￥平价套利￥￥￥￥￥￥￥￥￥￥￥ ')
                                                f.write('\n' + 'buy'+ OptionSubject_C + 'sell'+ FutureSubject)
                                                f.write('\n' + '期权买入价格a_C = ' + str(a_C) + '期货卖出价格b_Future = ' + str(b_Future) + '下单量V = ' + str(v))
                                                f.close()

                                        print("套利标的为" + OptionSubject_C)
                                        print("b_C=" + b_C)
                                        print("a_C=" + a_C)
                                        print("现货美元指数为" + str(index_btcusd))
                                        print("float(b_C)*index_btcusd=" + str(float(b_C) * index_btcusd))
                                        print("t1_a=" + str(t1_a))
                                        print("t1_b=" + str(t1_b))
                                        print("t2_a=" + str(t2_a))
                                        print("t2_b=" + str(t2_b))
                                        print("套利空间P等于=" + str(p))
                                        print("下单量V等于=" + str(v))
                                    elif t1_b > 0:
                                        if t1_b > t2_a:                                                   # 看涨期权被高估，卖出看涨期权，买入看跌期权。期货做多对冲
                                                p = t1_b - t2_a
                                                if p > Write_p:
                                                    textName = OptionTime + 'Par.txt'
                                                    f = open(textName, 'a')
                                                    f.write('\n' + str(p))
                                                    f.close()
                                                if p > Par_ProfitMin:

                                                        if 1000 * v > 10000 * (b_C - a_P):  # 期权每次下单量为v,期货需做多 1000*v，需做空10000*（a_P-b_C)。最终下单量为v_F.单位：张。
                                                            v_F = 1000 * v - 10000 * (b_C - a_P)
                                                        if 1000 * v < 10000 * (b_C - a_P):
                                                            v_F = 10000 * (b_C - a_P) - 1000 * v

                                                        btcNeed_Future = v_F*index_btcusdt/lever_future            # 交割合约下单所需保证金
                                                        if total_avail_balance_Future < 1.02 * btcNeed_Future:
                                                            print(timeNow, "@@@@@@@@@@@交割合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        btcNeed_maintenance_margin_C = (0.075 + float(mark_price_C)) * 0.1 * v             # 卖出看涨期权所需维持保证金
                                                        btcNeed_hold = (max(0.1,0.15 - (index_btcusd - exerciseprice_float)/mark_price_future) + float(mark_price_C))*0.1*v     #卖出看涨期权所需持仓保证金
                                                        btcNeed_Option_C = (max(btcNeed_hold - float(b_C)*0.1,btcNeed_maintenance_margin_C*0.1))*v            #卖出看涨期权所需挂单保证金

                                                        btcNeed_Option_P = float(a_P) *0.1*v                                                     #买入看跌期权所需挂单保证金，没考虑手续费
                                                        if total_avail_balance_Option < margin_Safe*(btcNeed_Option_C + btcNeed_Option_P):
                                                            print(timeNow, "@@@@@@@@@@@期权合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        print(timeNow,"-----可以平价套利了--￥￥￥------下单----￥￥￥-------")
                                                        try:
                                                            order_option = optionAPI.take_orders('BTC-USD', [
                                                                {"instrument_id": OptionSubject_C, "side": "sell", "price": b_C, "size": v, "order_type": "0", "match_price": "0"},
                                                                {"instrument_id": OptionSubject_P, "side": "buy", "price": a_P, "size": v, "order_type": "0", "match_price": "0"}
                                                            ])
                                                            if 1000 * v > 10000 * (b_C - a_P):
                                                                order_future = futureAPI.take_order(FutureSubject, '1', a_Future + order_protect, v_F, match_price='0')
                                                            if 1000 * v < 10000 * (b_C - a_P):
                                                                order_future = futureAPI.take_order(FutureSubject, '2', b_Future - order_protect, v_F, match_price='0')
                                                        except:
                                                            print(timeNow,"@@@@@@@下单失败@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue
                                                        Profit_Sum += p*v*0.1
                                                        Times_Sum += 1

                                                        textName_order = OptionTime + 'Orders.txt'                      # 下单信息写入文件
                                                        f = open(textName_order, 'a')
                                                        f.write('\n' + timeNow)
                                                        f.write('\n' + 'sell' + OptionSubject_C + 'buy' + OptionSubject_P + 'buy' + FutureSubject)
                                                        f.write('\n' + '期权sell价格b_C = ' + str(b_C) + '期权buy价格a_P = ' + str(a_P) + '期货buy价格a_Future = ' + str(a_Future) +'下单量V = ' + str(v))
                                                        f.close()

                                                print("套利标的为" + OptionSubject_C)
                                                print("b_C=" + b_C)
                                                print("a_C=" + a_C)
                                                print("b_P=" + b_P)
                                                print("a_P=" + a_P)
                                                print("现货美元指数为" + str(index_btcusd))
                                                print("float(b_C)*index_btcusd=" + str(float(b_C) * index_btcusd))
                                                print("float(a_P)*index_btcusd=" + str(float(a_P) * index_btcusd))
                                                print("t1_a=" + str(t1_a))
                                                print("t1_b=" + str(t1_b))
                                                print("t2_a=" + str(t2_a))
                                                print("t2_b=" + str(t2_b))
                                                print("套利空间P等于=" + str(p))
                                                print("下单量V等于=" + str(v))

                                        elif t2_b > t1_a:                                                          # 看跌期权被高估，卖出看跌期权，买入看涨期权。期货做空对冲
                                                p = t2_b - t1_a
                                                if p > Write_p:
                                                    textName = OptionTime + 'Par.txt'
                                                    f = open(textName, 'a')
                                                    f.write('\n' + str(p))
                                                    f.close()
                                                if p > Par_ProfitMin:

                                                        v_F = 1000 * v + 10000 * (b_P - a_C)  # 期权每次下单量为v,期货需做空 1000*v，需做空10000*（b_P - a_C)。最终下单量为v_F.单位：张。

                                                        btcNeed_Future = v_F*index_btcusdt/lever_future           # 交割合约下单所需保证金
                                                        if total_avail_balance_Future < 1.01 * btcNeed_Future:
                                                            print(timeNow, "@@@@@@@@@@@交割合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        btcNeed_maintenance_margin_P = (0.075 + 1.075 * mark_price_P) * 0.1 * v     # 卖出看跌期权所需维持保证金
                                                        btcNeed_hold = (max(0.1*(1 + mark_price_P),0.15 - (index_btcusd - exerciseprice_float)/mark_price_future) + mark_price_P)*0.1*v
                                                        btcNeed_Option_P = max(btcNeed_hold - float(b_P)*0.1,btcNeed_maintenance_margin_P*0.1)*v

                                                        btcNeed_Option_C= a_C * 0.1 * v                                             # 买入看涨期权所需挂单保证金，没考虑手续费
                                                        if total_avail_balance_Option < margin_Safe * (btcNeed_Option_P + btcNeed_Option_C):
                                                            print(timeNow, "@@@@@@@@@@@期权合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        print(timeNow,"-------可以平价套利了---￥￥￥----下单-----￥￥--" )

                                                        try:
                                                            order_option = optionAPI.take_orders('BTC-USD', [
                                                                {"instrument_id": OptionSubject_C, "side": "buy", "price": a_C, "size": v, "order_type": "0", "match_price": "0"},
                                                                {"instrument_id": OptionSubject_P, "side": "sell", "price": b_P, "size": v, "order_type": "0", "match_price": "0"}
                                                            ])

                                                            order_future = futureAPI.take_order(FutureSubject, '2', b_Future - order_protect, v_F, match_price='0')
                                                        except:
                                                            print(timeNow,"@@@@@@@@@@@下单失败@@@@@@@@@@")
                                                            continue
                                                        Profit_Sum += p*v*0.1
                                                        Times_Sum += 1

                                                        textName_order = OptionTime + 'Orders.txt'                              # 下单信息写入文件
                                                        f = open(textName_order, 'a')
                                                        f.write('\n' + timeNow)
                                                        f.write('\n' + 'sell' + OptionSubject_P + 'buy' + OptionSubject_C + 'sell' + FutureSubject)
                                                        f.write('\n' + '期权sell价格b_P = ' + str(b_P) + '期权buy价格a_C = ' + str(a_C) + '期货sell价格b_Future = ' + str(b_Future) + '下单量V = ' + str(v))
                                                        f.close()

                                                print("套利标的为" + OptionSubject_C)
                                                print("b_C=" + b_C)
                                                print("a_C=" + a_C)
                                                print("b_P=" + b_P)
                                                print("a_P=" + a_P)
                                                print("现货美元指数为" + str(index_btcusd))
                                                print("float(b_C)*index_btcusd=" + str(float(b_C) * index_btcusd))
                                                print("float(a_P)*index_btcusd=" + str(float(a_P) * index_btcusd))
                                                print("t1_a=" + str(t1_a))
                                                print("t1_b=" + str(t1_b))
                                                print("t2_a=" + str(t2_a))
                                                print("t2_b=" + str(t2_b))
                                                print("套利空间P等于=" + str(p))
                                                print("下单量V等于=" + str(v))
                            elif index_Future < exerciseprice_float:                                                         # 看跌期权为实值
                                    try:
                                        t1_a = float(a_P) * index_Future - (exerciseprice_float - index_Future)              # 计算看跌期权的时间价值
                                        t1_b = float(b_P) * index_Future - (exerciseprice_float - index_Future)
                                        t2_a = float(a_C) * index_Future                                                    # 计算看涨期权的时间价值
                                        t2_b = float(b_C) * index_Future
                                    except:
                                        print(timeNow,OptionSubject_C, "或",OptionSubject_P,"@@@@@@买一卖一价格或盘口深度为空@@@@@@@@")
                                        time.sleep(0.3)
                                        continue

                                    if t1_a < 0:                                                                           # 价格贴现套利。买入看跌期权，期货做多
                                        p = abs(t1_a)  # 计算标的套利空间
                                        if p > Write_p:
                                            textName = OptionTime + 'PriceDiscount.txt'
                                            f = open(textName, 'a')
                                            f.write('\n' + str(p))
                                            f.close()
                                        if p > PriceDiscount_ProfitMin:
                                            v_F = 1000 * v + 10000 * b_Future                        # 期权每次下单量为v,期货需做多 1000*v，需做多10000*b_Future。最终下单量为v_F.单位：张。
                                            btcNeed_Future = v_F*index_btcusdt/lever_future                    # 交割合约下单所需保证金
                                            if total_avail_balance_Future < 1.02 * btcNeed_Future:
                                                print(timeNow, "@@@@@@@@@@@交割合约账户余额不足@@@@@@@@@@")
                                                time.sleep(0.3)
                                                continue

                                            btcNeed_Option = float(a_P) * 0.1 * v                                       # 期权合约下单所需保证金
                                            if total_avail_balance_Option < 1.01 * btcNeed_Option:
                                                print(timeNow, "@@@@@@@@@@@期权合约账户余额不足@@@@@@@@@@")
                                                time.sleep(0.3)
                                                continue

                                            print(timeNow,"-----可以价格贴现套利咯-￥￥￥￥--下单--￥￥￥￥￥")
                                            try:
                                                order_option = optionAPI.take_order(instrument_id=OptionSubject_P,side= 'buy',order_type='0',price=a_P, size=v, match_price='0')
                                                order_future = futureAPI.take_order(FutureSubject, '1', a_Future + order_protect, v_F, match_price='0')
                                            except:
                                                print(timeNow,"@@@@@@@@@@@下单失败@@@@@@@@@@@")
                                                time.sleep(0.3)
                                                continue
                                            Profit_Sum += p*v*0.1
                                            Times_Sum += 1

                                            textName_order = OptionTime + 'Orders.txt'                                                  #下单信息写入文件
                                            f = open(textName_order, 'a')
                                            f.write('\n' + timeNow + '￥￥￥￥￥￥￥￥￥￥￥平价套利￥￥￥￥￥￥￥￥￥￥￥ ')
                                            f.write('\n' + 'buy' + OptionSubject_P + 'buy' + FutureSubject)
                                            f.write('\n' + '期权买入价格a_P = ' + str(a_P) + '期货买入价格a_Future = ' + str(a_Future) + '下单量V = ' + str(v))
                                            f.close()

                                        print("套利标的为" + OptionSubject_P)
                                        print("b_P=" + b_P)
                                        print("a_P=" + a_P)
                                        print("现货美元指数为" + str(index_btcusd))
                                        print("float(index_P)*b_Furure=" + str(float(b_P) * index_btcusd))
                                        print("t1_a=" + str(t1_a))
                                        print("t1_b=" + str(t1_b))
                                        print("t2_a=" + str(t2_a))
                                        print("t2_b=" + str(t2_b))
                                        print("套利空间P等于=" + str(p))
                                        print("下单量V等于=" + str(v))
                                    elif t1_b > 0:
                                        if t1_b > t2_a:                                                 #看跌期权被高估，卖出看跌期权，买入看涨期权。期货做空对冲
                                                p = t1_b - t2_a
                                                if p > Write_p:
                                                    textName = OptionTime + 'Par.txt'
                                                    f = open(textName, 'a')
                                                    f.write('\n' + str(p))
                                                    f.close()
                                                if p > Par_ProfitMin:

                                                        v_F = 1000 * v - 10000 * (b_P - a_C)  # 期权每次下单量为v,期货需做空 1000*v，需做空10000*（a_P-b_C)。最终下单量为v_F.单位：张。

                                                        btcNeed_Future = v_F*index_btcusdt / lever_future  # 交割合约下单所需保证金
                                                        if total_avail_balance_Future < 1.02 * btcNeed_Future:
                                                            print(timeNow, "@@@@@@@@@@@交割合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        btcNeed_maintenance_margin_P = (0.075 + 1.075 * mark_price_P) * 0.1 * v     # 卖出看跌期权所需维持保证金
                                                        btcNeed_hold = (max(0.1 * (1 + mark_price_P), 0.15 - (index_btcusd - exerciseprice_float) / mark_price_future) + mark_price_P) * 0.1 * v  # 卖出看跌期权所需持仓保证金
                                                        btcNeed_Option_P = max(btcNeed_hold - float(b_P) * 0.1,btcNeed_maintenance_margin_P * 0.1) * v          # 卖出看跌期权所需挂单保证金

                                                        btcNeed_Option_C = a_C * 0.1 * v                                                # 买入看涨期权所需挂单保证金，没考虑手续费
                                                        if total_avail_balance_Option < margin_Safe * (btcNeed_Option_P + btcNeed_Option_C):
                                                            print(timeNow, "@@@@@@@@@@@期权合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        print(timeNow,"--------可以平价套利了-----￥￥￥下单-----￥￥￥")
                                                        Profit_Sum += p*v*0.1
                                                        Times_Sum += 1

                                                        try:
                                                            order_option = optionAPI.take_orders('BTC-USD', [
                                                                {"instrument_id": OptionSubject_C, "side": "buy", "price": a_C, "size": v, "order_type": "0", "match_price": "0"},
                                                                {"instrument_id": OptionSubject_P, "side": "sell", "price": b_P, "size": v, "order_type": "0", "match_price": "0"}
                                                            ])
                                                            order_future = futureAPI.take_order(FutureSubject, '2', b_Future - order_protect, v_F, match_price='0')
                                                        except:
                                                            print(timeNow,"@@@@@@@@@@@@@下单失败@@@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue
                                                        Profit_Sum += p*v*0.1
                                                        Times_Sum += 1

                                                        textName_order = OptionTime + 'Orders.txt'                      # 下单信息写入文件,以便数据分析
                                                        f = open(textName_order, 'a')
                                                        f.write('\n' + timeNow)
                                                        f.write('\n' + 'sell' + OptionSubject_P + 'buy' + OptionSubject_C + 'sell' + FutureSubject)
                                                        f.write('\n' + '期权sell价格b_P = ' + str(b_P) + '期权buy价格a_C = ' + str(a_C) + '期货sell价格b_Future = ' + str(b_Future) + '下单量V = ' + str(v))
                                                        f.close()

                                                print("套利标的为" + OptionSubject_C)
                                                print("b_C=" + b_C)
                                                print("a_C=" + a_C)
                                                print("b_P=" + b_P)
                                                print("a_P=" + a_P)
                                                print("现货美元指数为" + str(index_btcusd))
                                                print("float(b_P)*index_btcusd=" + str(float(b_P) * index_btcusd))
                                                print("float(a_C)*index_btcusd=" + str(float(a_C) * index_btcusd))
                                                print("t1_a=" + str(t1_a))
                                                print("t1_b=" + str(t1_b))
                                                print("t2_a=" + str(t2_a))
                                                print("t2_b=" + str(t2_b))

                                                print("套利空间P等于=" + str(p))
                                                print("下单量V等于=" + str(v))
                                        elif t2_b > t1_a:                                                          #看涨期权被高估，卖出看涨期权，买入看跌期权。期货做多对冲
                                                p = t2_b - t1_a
                                                if p > Write_p:
                                                    textName = OptionTime + 'Par.txt'
                                                    f = open(textName, 'a')
                                                    f.write('\n' + str(p))
                                                    f.close()
                                                if p > Par_ProfitMin:
                                                        if 1000 * v > 10000 * (b_C - a_P):  # 期权每次下单量为v,期货需做多 1000*v，需做空10000*（b_C - a_P)。最终下单量为v_F.单位：张。
                                                            v_F = 1000 * v - 10000 * (b_C - a_P)
                                                        if 1000 * v < 10000 * (b_C - a_P):
                                                            v_F = 10000 * (b_C - a_P) - 1000 * v

                                                        btcNeed_Future = v_F * index_btcusdt / lever_future  # 交割合约下单所需保证金
                                                        if total_avail_balance_Future < 1.02 * btcNeed_Future:
                                                            print(timeNow, "@@@@@@@@@@@交割合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        btcNeed_maintenance_margin_C = (0.075 + float(mark_price_C)) * 0.1 * v  # 卖出看涨期权所需维持保证金
                                                        btcNeed_hold = (max(0.1, 0.15 - (index_btcusd - exerciseprice_float) / mark_price_future) + float(mark_price_C)) * 0.1 * v  # 卖出看涨期权所需持仓保证金
                                                        btcNeed_Option_C = (max(btcNeed_hold - float(b_C) * 0.1,btcNeed_maintenance_margin_C * 0.1)) * v  # 卖出看涨期权所需挂单保证金

                                                        btcNeed_Option_P = float(a_P) * 0.1 * v  # 买入看跌期权所需挂单保证金，没考虑手续费
                                                        if total_avail_balance_Option < margin_Safe * (btcNeed_Option_C + btcNeed_Option_P):
                                                            print(timeNow, "@@@@@@@@@@@期权合约账户余额不足@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue

                                                        print(timeNow,"--------可以平价套利了------￥￥￥￥￥下单-----￥￥￥￥￥")
                                                        try:
                                                            order_option = optionAPI.take_orders('BTC-USD', [
                                                                {"instrument_id": OptionSubject_C, "side": "sell", "price": b_C, "size": v, "order_type": "0", "match_price": "0"},
                                                                {"instrument_id": OptionSubject_P, "side": "buy", "price": a_P, "size": v, "order_type": "0", "match_price": "0"}
                                                            ])
                                                            if 1000 * v > 10000 * (b_P - a_C):
                                                                order_future = futureAPI.take_order(FutureSubject, '1', a_Future + order_protect,v , match_price='0')
                                                            if 1000 * v < 10000 * (b_P - a_C):
                                                                order_future = futureAPI.take_order(FutureSubject, '2', b_Future - order_protect, v, match_price='0')
                                                        except:
                                                            print(timeNow,"@@@@@@@@@@@下单失败@@@@@@@@@@@")
                                                            time.sleep(0.3)
                                                            continue
                                                        Profit_Sum += p*v*0.1
                                                        Times_Sum += 1

                                                        textName_order = OptionTime + 'Orders.txt'  # 下单信息写入文件
                                                        f = open(textName_order, 'a')
                                                        f.write('\n' + timeNow)
                                                        f.write('\n' + 'sell' + OptionSubject_C + 'buy' + OptionSubject_P + 'buy' + FutureSubject)
                                                        f.write('\n' + '期权sell价格b_C = ' + str(b_C) + '期权buy价格a_P = ' + str(a_P) + '期货buy价格a_Future = ' + str(a_Future) + '下单量V = ' + str(v))
                                                        f.close()

                                                print("套利标的为" + OptionSubject_C)
                                                print("b_C=" + b_C, "a_C=" + a_C, "b_P=" + b_P, "a_P=" + a_P)
                                                print("现货美元指数为" + str(index_btcusd))
                                                print("float(b_P)*index_Furure=" + str(float(b_P) * index_btcusd))
                                                print("float(a_C)*index_Furure=" + str(float(a_C) * index_btcusd))
                                                print("t1_a=" + str(t1_a))
                                                print("t1_b=" + str(t1_b))
                                                print("t2_a=" + str(t2_a))
                                                print("t2_b=" + str(t2_b))
                                                print("套利空间P等于=" + str(p))
                                                print("下单量V等于=" + str(v))
            # time.sleep(0.2)
        print("the Sum of Profit =" + str(Profit_Sum))
        print("the Times of action =" + str(Times_Sum))
        print("the Times of e =" + str(badTimes))
        time.sleep(0.2)



