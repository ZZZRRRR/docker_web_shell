from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import asyncio

#计时ws的连接时间，30分钟没有websocket的数据传输就自动断开
class timer():

    executors = {
    'default': ThreadPoolExecutor(100)
  }

    def start(self, action_check, action_set, close,loop):
        scheduler = BackgroundScheduler(executors=timer.executors)
      # 添加定时任务
        self.job = scheduler.add_job(self.action, 'interval', seconds=60,
                         args=[action_check, action_set, close,loop])
        scheduler.start()

    def action(self, action_check, action_set, close,loop):
        if action_check():
            action_set()
        else:
            #关闭websocket连接
            asyncio.set_event_loop(loop)
            close()

    def remove(self):
      #移除计时任务
        self.job.remove()


#计时websocket的连接校验，防止连接不发送token验证的恶意链接
class start_timer():
  executors = {
    "default": ThreadPoolExecutor(100)
  }

  def start(self,close,loop):
      scheduler = BackgroundScheduler(executors=start_timer.executors)
      self.job = scheduler.add_job(self.action, 'interval',seconds=5,args=[close,loop])
      scheduler.start()

  def action(self,close,loop):
    #   关闭websocket连接
      self.job.remove()
      asyncio.set_event_loop(loop)
      close()

  def remove(self):
      #移除计时任务
      self.job.remove()