"""
验证码管理器模块：提供文字点击验证功能

本模块主要功能:
1. 文字点击验证：生成包含"天远数据"四个字的图片，用户依次点击
2. 防机器人验证：通过轨迹分析和行为特征防止自动破解
"""

import os
import time
import random
import base64
import uuid
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from cryptography.fernet import Fernet
import logging

from django.conf import settings
from .models import SliderCaptcha

logger = logging.getLogger(__name__)

class CaptchaType:
    """验证码类型枚举"""
    TEXT_CLICK = 'text'    # 文字点击类型
    SLIDER = 'slider'      # 滑块类型（保留兼容性，不再主动使用）

class CaptchaManager:
    """验证码管理器：专注于文字点击验证"""

    def __init__(self):
        # 验证码有效期(秒)
        self.expiry_seconds = 300
        # 文字点击误差范围(像素)
        self.text_click_error_range = 20
        # 最大验证尝试次数
        self.max_attempts = 5
        # 获取或创建加密密钥
        self._get_encryption_key()
        # 图片文件夹路径
        self.bg_dir = os.path.join(settings.MEDIA_ROOT, 'captcha', 'bg')
        # 字体文件路径
        self.font_path = os.path.join(settings.MEDIA_ROOT, 'captcha', 'fonts', 'simhei.ttf')
        
        # 确保目录存在
        os.makedirs(self.bg_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.font_path), exist_ok=True)
        
        # 如果没有字体文件，尝试查找系统字体
        if not os.path.exists(self.font_path):
            system_fonts = [
                '/usr/share/fonts/truetype/droid/SIMSUN.TTC',  # Linux
                'C:\\Windows\\Fonts\\simhei.ttf',  # Windows
                '/System/Library/Fonts/PingFang.ttc'  # macOS
            ]
            for font in system_fonts:
                if os.path.exists(font):
                    self.font_path = font
                    break

    def _get_encryption_key(self):
        """获取或创建用于加密验证码位置的密钥"""
        key = getattr(settings, 'CAPTCHA_KEY', None)
        if not key:
            # 如果未配置密钥，使用默认密钥
            # 注意：生产环境应在settings中配置固定的密钥
            key = b'TrFKx_K09RI0rY77zT1NQONUTWzT8-SEAGYcNCq2EfM='

        self.fernet = Fernet(key)

    def _get_random_bg_image(self):
        """获取随机背景图片"""
        # 如果没有预设图片，生成基本图片
        if not os.path.exists(self.bg_dir) or len(os.listdir(self.bg_dir)) == 0:
            # 创建一个随机颜色的背景图
            width, height = 300, 150
            bg_image = Image.new('RGB', (width, height), (random.randint(200, 255),
                                                          random.randint(200, 255),
                                                          random.randint(200, 255)))
            # 画一些随机线条
            draw = ImageDraw.Draw(bg_image)
            for _ in range(5):
                start_point = (random.randint(0, width), random.randint(0, height))
                end_point = (random.randint(0, width), random.randint(0, height))
                draw.line([start_point, end_point], fill=(random.randint(100, 150),
                                                          random.randint(100, 150),
                                                          random.randint(100, 150)),
                          width=2)

            return bg_image

        # 从预设图片中随机选择一张
        bg_files = os.listdir(self.bg_dir)
        bg_file = random.choice(bg_files)
        bg_path = os.path.join(self.bg_dir, bg_file)

        return Image.open(bg_path)
        
    def _create_text_click_image(self, bg_image):
        """创建文字点击验证码图片
        
        在背景图上随机位置绘制"天远大数据"五个字，
        用户需要依次点击这些文字
        
        Args:
            bg_image: 背景图片
            
                    Returns:
                dict: {
                    'bg_with_text': 带文字的背景图,
                    'positions': 五个字的位置列表 [(x1,y1), (x2,y2), (x3,y3), (x4,y4), (x5,y5)]
                }
        """
        width, height = bg_image.size
        
        # 创建绘图对象
        bg_with_text = bg_image.copy()
        draw = ImageDraw.Draw(bg_with_text)
        
        # 文字内容和颜色
        text = "天远大数据"
        colors = [
            (255, 0, 0),    # 红
            (0, 0, 255),    # 蓝
            (0, 128, 0),    # 绿
            (128, 0, 128),   # 紫
            (255, 140, 0)    # 橙
        ]
        random.shuffle(colors)  # 随机打乱颜色
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font_size = 30
            font = ImageFont.truetype(self.font_path, font_size)
        except Exception as e:
            logger.warning(f"无法加载字体文件: {str(e)}，使用默认字体")
            # 使用PIL默认字体
            font = ImageFont.load_default()
            font_size = 20
        
        # 计算字符边界以防止重叠
        min_distance = font_size + 10  # 字符之间的最小距离
        
        # 随机生成5个字的位置
        positions = []
        char_sizes = []  # 存储字符尺寸以供验证使用
        
        for i in range(5):
            attempts = 0
            while attempts < 50:  # 最多尝试50次找位置
                # 确保字符不靠近边缘
                x = random.randint(font_size, width - font_size)
                y = random.randint(font_size, height - font_size)
                
                # 检查是否与其他字符重叠
                too_close = False
                for pos in positions:
                    distance = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
                    if distance < min_distance:
                        too_close = True
                        break
                
                if not too_close:
                    positions.append((x, y))
                    
                    # 估算汉字宽高
                    char_width = font_size
                    char_height = font_size
                    
                    # 尝试使用更精确的测量方法
                    try:
                        if hasattr(font, 'getbbox'):
                            bbox = font.getbbox(text[i])
                            char_width = bbox[2] - bbox[0]
                            char_height = bbox[3] - bbox[1]
                        elif hasattr(font, 'getsize'):
                            char_width, char_height = font.getsize(text[i])
                    except:
                        # 如果测量失败，使用默认估算
                        pass
                        
                    char_sizes.append((char_width, char_height))
                    break
                    
                attempts += 1
            
            # 如果找不到合适位置，强制放置
            if attempts >= 50:
                x = width // 5 + i * (width // 5)
                y = height // 2 + random.randint(-20, 20)
                positions.append((x, y))
                char_sizes.append((font_size, font_size))
        
        # 绘制文字
        for i, (x, y) in enumerate(positions):
            # 在文字周围添加干扰线和噪点，增加识别难度
            for _ in range(2):
                x1 = x - random.randint(5, 15)
                y1 = y - random.randint(5, 15)
                x2 = x + random.randint(5, 15)
                y2 = y + random.randint(5, 15)
                draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0), width=1)
            
            # 绘制文字，居中于指定坐标
            char = text[i]
            # 绘制阴影增强可读性
            draw.text((x+1, y+1), char, font=font, fill=(0, 0, 0))
            draw.text((x, y), char, font=font, fill=colors[i])
        
        # 添加干扰元素：随机线条和圆点
        for _ in range(10):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 200), 
                                                random.randint(0, 200), 
                                                random.randint(0, 200)), width=1)
            
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(1, 3)
            draw.ellipse((x-r, y-r, x+r, y+r), 
                        fill=(random.randint(0, 200), 
                              random.randint(0, 200), 
                              random.randint(0, 200)))
        
        # 保存位置和字符尺寸信息
        self.char_sizes = char_sizes
        
        return {
            'bg_with_text': bg_with_text,
            'positions': positions
        }

    def _image_to_base64(self, image):
        """将PIL图像转换为base64字符串"""
        buffered = BytesIO()
        # 保存图像到内存中
        if image.mode == 'RGBA':
            image.save(buffered, format="PNG")
        else:
            image.save(buffered, format="JPEG", quality=85)
        # 获取base64编码
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 添加适当的数据URI前缀
        if image.mode == 'RGBA':
            return f"data:image/png;base64,{img_str}"
        else:
            return f"data:image/jpeg;base64,{img_str}"
            
    def _encrypt_positions(self, positions):
        """加密文字点击位置信息列表"""
        positions_json = json.dumps({'positions': positions})
        encrypted = self.fernet.encrypt(positions_json.encode())
        return encrypted.decode()
            
    def _decrypt_positions(self, encrypted_positions):
        """解密文字点击位置信息列表"""
        try:
            decrypted = self.fernet.decrypt(encrypted_positions.encode())
            positions_data = json.loads(decrypted)
            return positions_data.get('positions')
        except Exception as e:
            logger.error(f"解密验证码位置失败: {str(e)}")
            return None
            
    def _validate_text_clicks(self, clicks, expected_positions):
        """
        验证文字点击是否正确
        
        Args:
            clicks: 用户点击坐标列表 [{"x": x1, "y": y1, "t": t1}, ...]
            expected_positions: 预期的文字位置列表 [(x1,y1), (x2,y2), ...]
            
        Returns:
            bool: 是否验证通过
        """
        # 检查点击次数是否正确
        print(f"验证点击: 用户点击 {len(clicks)} 次, 需要点击 {len(expected_positions)} 次")
        if len(clicks) != len(expected_positions):
            print(f"点击次数不匹配: 预期={len(expected_positions)}, 实际={len(clicks)}")
            return False
            
        # 获取字符尺寸（如果没有，使用默认值）
        char_sizes = getattr(self, 'char_sizes', [(30, 30)] * len(expected_positions))
            
        # 检查点击顺序和位置是否正确（区域判断）
        for i, click in enumerate(clicks):
            x = click.get('x', 0)
            y = click.get('y', 0)
            
            # 获取预期位置和字符尺寸
            center_x, center_y = expected_positions[i]
            char_width, char_height = char_sizes[i] if i < len(char_sizes) else (30, 30)
            
            # 计算文字区域边界（考虑误差范围）
            half_width = char_width / 2 + self.text_click_error_range
            half_height = char_height / 2 + self.text_click_error_range
            
            # 判断点击是否在扩展后的文字区域内
            in_x_range = center_x - half_width <= x <= center_x + half_width
            in_y_range = center_y - half_height <= y <= center_y + half_height
            
            # 计算点击位置与文字中心的距离，用于日志记录
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            
            print(f"第 {i+1} 次点击: 用户=({x}, {y}), 文字中心=({center_x}, {center_y}), 距离={distance:.2f}")
            print(f"文字区域: 宽={char_width}, 高={char_height}, 扩展误差={self.text_click_error_range}")
            
            # 如果点击不在文字区域范围内，验证失败
            if not (in_x_range and in_y_range):
                print(f"第 {i+1} 次点击不在文字区域范围内")
                return False
                
        # 检查点击时间间隔是否合理并分析点击模式
        time_intervals = []
        
        for i in range(1, len(clicks)):
            prev_time = clicks[i-1].get('t', 0)
            curr_time = clicks[i].get('t', 0)
            time_diff = curr_time - prev_time
            time_intervals.append(time_diff)
            
            print(f"点击间隔 {i} -> {i+1}: {time_diff} ms")
            
            # 两次点击间隔过短(<200ms)被视为可疑
            if time_diff < 200:
                print(f"点击间隔过短: {time_diff} ms < 200 ms")
                return False
        
        print("所有验证通过!")
        return True

    def generate_captcha(self, client_fingerprint, client_ip=''):
        """
        生成文字点击验证码
        
        Args:
            client_fingerprint: 客户端指纹
            client_ip: 客户端IP
            
        Returns:
            验证码数据字典
        """
        # 检查同一个指纹是否存在尝试次数过多的验证码，如果有，将其标记为过期
        try:
            failed_captchas = SliderCaptcha.objects.filter(
                client_fingerprint=client_fingerprint,
                is_verified=False,
                attempts__gte=self.max_attempts,
                expire_time__gt=int(time.time())
            )
            
            # 将这些验证码标记为过期
            if failed_captchas.exists():
                current_time = int(time.time())
                failed_captchas.update(expire_time=current_time)
                print(f"已将 {failed_captchas.count()} 个验证失败的验证码标记为过期")
        except Exception as e:
            print(f"检查失败验证码时出错: {str(e)}")
        
        # 获取随机背景图
        bg_image = self._get_random_bg_image()
        
        token = str(uuid.uuid4())
        current_time = int(time.time())
        
        # 创建文字点击验证码
        result = self._create_text_click_image(bg_image)
        
        # 加密正确的文字位置
        encrypted_positions = self._encrypt_positions(result['positions'])
        
        # 转换图片为base64编码
        bg_base64 = self._image_to_base64(result['bg_with_text'])
        
        # 保存验证码记录到数据库
        captcha = SliderCaptcha(
            token=token,
            bg_image=bg_base64,
            slider_image='',  # 文字点击验证码不需要滑块图片
            correct_position=encrypted_positions,  # 复用字段存储文字位置
            client_fingerprint=client_fingerprint,
            last_attempt_ip=client_ip,
            create_time=current_time,
            expire_time=current_time + self.expiry_seconds
        )
        
        try:
            captcha.save()
        except Exception as e:
            print(f"保存验证码记录失败: {str(e)}")
            # 如果保存失败（如数据太长），尝试使用简化的位置数据
            try:
                # 简化位置数据，只保留坐标
                simplified_positions = [(x, y) for x, y in result['positions']]
                encrypted_positions = self._encrypt_positions(simplified_positions)
                
                captcha.correct_position = encrypted_positions
                captcha.save()
            except Exception as inner_e:
                print(f"使用简化位置数据保存仍然失败: {str(inner_e)}")
                # 如果仍然失败，返回一个错误
                return None
        
        # 打印生成的验证码位置信息
        print(f"生成验证码: token={token}, 位置={result['positions']}")
        
        return {
            'type': CaptchaType.TEXT_CLICK,
            'token': token,
            'bg_image': bg_base64,
            'prompt': '请依次点击 "天" "远" "大" "数" "据" 五个字'
        }

    def verify_captcha(self, token, client_ip='', client_fingerprint='', clicks=None):
        """
        验证用户输入是否正确
        
        Args:
            token: 验证码token
            client_ip: 客户端IP
            client_fingerprint: 客户端指纹
            clicks: 点击位置列表
            
        Returns:
            (bool, str): (验证是否成功, 消息)
        """
        try:
            print(f"开始验证: token={token}, ip={client_ip}, 点击数据长度={len(clicks) if clicks else 0}")
            
            # 查询验证码记录
            try:
                captcha = SliderCaptcha.objects.get(token=token)
                print(f"验证码记录: is_verified={captcha.is_verified}, attempts={captcha.attempts}")
            except SliderCaptcha.DoesNotExist:
                print(f"验证码不存在: token={token}")
                return False, "验证码不存在或已过期"

            # 检查验证码是否已被验证
            if captcha.is_verified:
                print(f"验证码已被使用: token={token}")
                return False, "验证码已被使用"

            # 检查验证码是否过期
            current_time = int(time.time())
            if current_time > captcha.expire_time:
                print(f"验证码已过期: 当前时间={current_time}, 过期时间={captcha.expire_time}")
                return False, "验证码已过期"

            # 检查尝试次数是否超过限制
            if captcha.attempts >= self.max_attempts:
                print(f"验证次数过多: attempts={captcha.attempts} >= max={self.max_attempts}")
                # 将验证码标记为过期，防止继续使用
                captcha.expire_time = current_time - 1
                captcha.save(update_fields=['expire_time'])
                return False, "验证次数过多，请重新获取验证码"

            # 检查客户端指纹是否一致(如果有指纹)
            if captcha.client_fingerprint and client_fingerprint and captcha.client_fingerprint != client_fingerprint:
                print(f"客户端指纹不匹配: 验证码={captcha.client_fingerprint}, 请求={client_fingerprint}")
                captcha.attempts += 1
                captcha.last_attempt_ip = client_ip
                captcha.save(update_fields=['attempts', 'last_attempt_ip'])
                return False, "客户端环境发生变化，请重新获取验证码"

            # 更新验证尝试次数和IP
            captcha.attempts += 1
            captcha.last_attempt_ip = client_ip
            
            # 文字点击验证码验证
            if not clicks:
                print("缺少点击数据")
                captcha.save(update_fields=['attempts', 'last_attempt_ip'])
                return False, "缺少点击数据"
                
            # 解密正确的点击位置
            expected_positions = self._decrypt_positions(captcha.correct_position)
            if expected_positions is None:
                print("解密位置失败")
                return False, "验证码数据错误"
            
            print(f"解密位置成功: {expected_positions}")
            
            # 验证点击是否正确
            validation_result = self._validate_text_clicks(clicks, expected_positions)
            if validation_result:
                # 验证成功
                print("验证成功")
                captcha.is_verified = True
                captcha.verify_time = current_time
                captcha.save(update_fields=['is_verified', 'verify_time', 'attempts', 'last_attempt_ip'])
                return True, "验证成功"
            else:
                # 验证失败
                print("验证失败")
                captcha.save(update_fields=['attempts', 'last_attempt_ip'])
                
                # 如果已经达到最大尝试次数，标记为过期
                if captcha.attempts >= self.max_attempts:
                    print(f"已达到最大尝试次数，标记验证码为过期")
                    captcha.expire_time = current_time - 1
                    captcha.save(update_fields=['expire_time'])
                    return False, "验证次数过多，请重新获取验证码"
                    
                return False, "点击错误，请重新尝试"

        except Exception as e:
            print(f"验证异常: {str(e)}")
            return False, "验证过程发生错误"


# 全局验证码管理器实例
captcha_manager = CaptchaManager()


