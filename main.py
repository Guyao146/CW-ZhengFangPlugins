import requests
import json
import time
from datetime import datetime
from PyQt5.QtCore import QTimer

class ZhengFangPlugin:
    def __init__(self, settings):
        self.settings = settings
        self.session = requests.Session()
        self.timer = QTimer()
        
        # 初始化自动同步
        if self.settings['auto_sync']:
            self.start_auto_sync()
            
    def login(self):
        """登录正方系统"""
        login_url = f"{self.settings['api_url']}/login"
        payload = {
            'username': self.settings['username'],
            'password': self.settings['password']
        }
        
        try:
            response = self.session.post(login_url, data=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"登录失败: {e}")
            return False
            
    def get_schedule(self):
        """获取课表数据"""
        if not self.login():
            return None
            
        schedule_url = f"{self.settings['api_url']}/schedule"
        try:
            response = self.session.get(schedule_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取课表失败: {e}")
            return None
            
    def parse_schedule(self, data):
        """解析课表数据"""
        schedule = []
        for course in data['courses']:
            schedule.append({
                'name': course['name'],
                'teacher': course['teacher'],
                'time': course['time'],
                'location': course['location']
            })
        return schedule
        
    def save_schedule(self, schedule):
        """保存课表数据"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"schedule_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
            
    def start_auto_sync(self):
        """启动自动同步"""
        self.timer.timeout.connect(self.sync_schedule)
        self.timer.start(3600000)  # 每小时同步一次
        
    def sync_schedule(self):
        """同步课表"""
        print("开始同步课表...")
        data = self.get_schedule()
        if data:
            schedule = self.parse_schedule(data)
            self.save_schedule(schedule)
            print("课表同步完成")
            
def main(settings):
    plugin = ZhengFangPlugin(settings)
    # 首次启动时立即同步
    plugin.sync_schedule()
