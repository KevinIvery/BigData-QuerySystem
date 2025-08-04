"""
PDF授权书生成工具
"""
import os
import hashlib
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black

class AuthorizationPDFGenerator:
    """PDF授权书生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_fonts()
    
    def _setup_fonts(self):
        """设置中文字体"""
        try:
            # 优先使用当前目录的simsun.ttc字体
            current_dir = os.path.dirname(os.path.abspath(__file__))
            simsun_path = os.path.join(current_dir, 'simsun.ttc')
            
            if os.path.exists(simsun_path):
                pdfmetrics.registerFont(TTFont('SimSun', simsun_path))
                print(f"[AuthorizationPDFGenerator] 成功加载当前目录字体: {simsun_path}")
            else:
                # 备用字体路径
                font_paths = [
                    '/System/Library/Fonts/PingFang.ttc',  # macOS
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                    'C:/Windows/Fonts/simsun.ttc',  # Windows
                    'C:/Windows/Fonts/msyh.ttc',  # Windows 微软雅黑
                ]
                
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('SimSun', font_path))
                        print(f"[AuthorizationPDFGenerator] 成功加载系统字体: {font_path}")
                        break
                else:
                    # 如果没有找到中文字体，使用默认字体
                    print("[AuthorizationPDFGenerator] 未找到中文字体，将使用默认字体")
        except Exception as e:
            print(f"[AuthorizationPDFGenerator] 字体设置失败: {str(e)}")
    
    def generate_authorization_pdf(self, name, id_card, company_name, file_path):
        """
        生成PDF授权书
        
        Args:
            name: 用户姓名
            id_card: 身份证号
            company_name: 公司名称
            file_path: PDF文件保存路径
            
        Returns:
            dict: 包含生成结果和文件哈希
        """
        try:
            # 创建PDF文档
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # 构建PDF内容
            story = []
            
            # 标题样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
                fontName='SimSun' if 'SimSun' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 正文样式
            body_style = ParagraphStyle(
                'CustomBody',
                parent=self.styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                leading=18,
                fontName='SimSun' if 'SimSun' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 签名样式
            signature_style = ParagraphStyle(
                'CustomSignature',
                parent=self.styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                leading=18,
                fontName='SimSun' if 'SimSun' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            )
            
            # 添加标题
            story.append(Paragraph("数据查询授权书", title_style))
            story.append(Spacer(1, 20))
            
            # 添加致送单位
            story.append(Paragraph(f"致：{company_name}", body_style))
            story.append(Spacer(1, 20))
            
            # 添加正文
            content_parts = [
                f"本人，<strong>{name}</strong>（身份证号码：<strong>{id_card}</strong>），在此确认并同意，为使用贵平台提供的大数据查询服务，本人自愿、明确且不可撤销地授权贵公司及贵公司合作的第三方数据服务机构，依据本授权书查询、核验、处理与本人相关的，为完成风险评估所必需的个人信息（包括但不限于个人基本信息、司法涉诉信息、信贷风险信息等）。",
                "",
                "本人同意贵公司将前述查询到的信息及数据分析结果，通过平台向本人展示，用于本人了解自身信用状况、进行风险评估等合法合规用途。",
                "",
                "本人知晓并同意，本授权是提供服务所必需。本授权自本人签署之日（即点击\"同意\"按钮之日）起生效，至本人注销平台账户之日止。本人已仔细阅读并完全理解本授权书的全部内容。",
                "",
                "<strong>本人确认，同意本授权书即视为本人以电子文档方式签署，本授权书将以电子档案形式留存，与纸质授权书具有同等法律效力，可作为处理相关争议的有效依据。</strong>",
                "",
                "",
                f"授权人：{name}",
                f"日期：{datetime.now().strftime('%Y年%m月%d日')}"
            ]
            
            for part in content_parts:
                if part.strip():
                    if part.startswith("授权人：") or part.startswith("日期："):
                        story.append(Paragraph(part, signature_style))
                    else:
                        story.append(Paragraph(part, body_style))
                else:
                    story.append(Spacer(1, 12))
            
            # 生成PDF
            doc.build(story)
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)
            
            print(f"[AuthorizationPDFGenerator] PDF授权书生成成功: {file_path}")
            
            return {
                'success': True,
                'file_path': file_path,
                'file_hash': file_hash
            }
            
        except Exception as e:
            print(f"[AuthorizationPDFGenerator] PDF授权书生成失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_file_hash(self, file_path):
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                return hashlib.md5(file_content).hexdigest()
        except Exception as e:
            print(f"[AuthorizationPDFGenerator] 计算文件哈希失败: {str(e)}")
            return ""
    
    def get_authorization_content(self, name, id_card, company_name):
        """
        生成授权书文本内容
        
        Args:
            name: 用户姓名
            id_card: 身份证号
            company_name: 公司名称
            
        Returns:
            str: 授权书文本内容
        """
        current_date = datetime.now().strftime('%Y年%m月%d日')
        
        content = f"""数据查询授权书

致：{company_name}

本人，{name}（身份证号码：{id_card}），在此确认并同意，为使用贵平台提供的大数据查询服务，本人自愿、明确且不可撤销地授权贵公司及贵公司合作的第三方数据服务机构，依据本授权书查询、核验、处理与本人相关的，为完成风险评估所必需的个人信息（包括但不限于个人基本信息、司法涉诉信息、信贷风险信息等）。

本人同意贵公司将前述查询到的信息及数据分析结果，通过平台向本人展示，用于本人了解自身信用状况、进行风险评估等合法合规用途。

本人知晓并同意，本授权是提供服务所必需。本授权自本人签署之日（即点击"同意"按钮之日）起生效，至本人注销平台账户之日止。本人已仔细阅读并完全理解本授权书的全部内容。

本人确认，同意本授权书即视为本人以电子文档方式签署，本授权书将以电子档案形式留存，与纸质授权书具有同等法律效力，可作为处理相关争议的有效依据。

授权人：{name}
日期：{current_date}"""
        
        return content 