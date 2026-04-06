"""音效管理器"""
import pygame
import os
import math
import array

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except:
            self.enabled = False
            print("⚠️ 音效初始化失败")
            return
        
        self.sounds = {}
        self.generate_sounds()
    
    def generate_sounds(self):
        """生成合成音效"""
        if not self.enabled:
            return
        
        # 射击音效（短促高音）
        self.sounds['shoot'] = self.generate_tone(880, 0.05, 0.3)
        
        # 击中音效（下降音）
        self.sounds['hit'] = self.generate_tone(440, 0.08, 0.2, freq_decay=0.5)
        
        # 建造塔音效（上升音）
        self.sounds['build'] = self.generate_tone(330, 0.15, 0.4, freq_inc=1.5)
        
        # 升级音效（双音）
        self.sounds['upgrade'] = self.generate_tone(523, 0.1, 0.5)
        
        # 卖出音效（下降）
        self.sounds['sell'] = self.generate_tone(440, 0.12, 0.3, freq_decay=0.3)
        
        # 金币音效
        self.sounds['coin'] = self.generate_tone(1200, 0.08, 0.5)
        
        # 波次开始
        self.sounds['wave_start'] = self.generate_tone(262, 0.2, 0.6)
        
        # 暴击
        self.sounds['crit'] = self.generate_tone(880, 0.15, 0.7)
        
        # 胜利
        self.sounds['victory'] = self.generate_tone(523, 0.3, 0.8)
        
        # 失败
        self.sounds['defeat'] = self.generate_tone(200, 0.4, 0.5, freq_decay=0.2)
    
    def generate_tone(self, freq, duration, volume=0.5, freq_decay=1.0, freq_inc=1.0):
        """生成单音调"""
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            
            samples = []
            for i in range(n_samples):
                t = i / sample_rate
                # 频率变化
                if freq_decay < 1.0:
                    f = freq * (freq_decay + (1 - freq_decay) * (i / n_samples))
                elif freq_inc > 1.0:
                    f = freq * (1 + (freq_inc - 1) * (i / n_samples))
                else:
                    f = freq
                
                # 正弦波 + 淡出
                wave = math.sin(2 * math.pi * f * t)
                envelope = 1.0 - (i / n_samples)  # 淡出
                sample = int(wave * envelope * volume * 32767)
                samples.append(sample)
            
            # 转为立体声
            stereo = []
            for s in samples:
                stereo.append(s)
                stereo.append(s)
            
            return pygame.mixer.Sound(buffer=array.array('h', stereo))
        except:
            return None
    
    def play(self, name):
        """播放音效"""
        if self.enabled and name in self.sounds and self.sounds[name]:
            self.sounds[name].play()
    
    def toggle(self):
        """切换音效开关"""
        self.enabled = not self.enabled
        return self.enabled