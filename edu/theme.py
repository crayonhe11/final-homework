"""本地桌面设计系统：固定导航、卡片、主次操作和统一文字层级。"""
from tkinter import ttk

BG = '#f5f6fa'
INK = '#20263d'
MUTED = '#758096'
ACCENT = '#6555d9'
BORDER = '#e3e7ef'


def apply_theme(root):
    style=ttk.Style(root)
    style.theme_use('clam')
    style.configure('.',font=('Arial',12),background=BG,foreground=INK)
    style.configure('TFrame',background=BG)
    style.configure('TLabel',background=BG,foreground=INK)
    style.configure('Muted.TLabel',foreground=MUTED,font=('Arial',11))
    style.configure('Title.TLabel',font=('Arial',24,'bold'))
    style.configure('Card.TFrame',background='white')
    style.configure('Card.TLabel',background='white')
    style.configure('CardTitle.TLabel',background='white',font=('Arial',16,'bold'))
    style.configure('CardMuted.TLabel',background='white',foreground=MUTED,font=('Arial',11))
    style.configure('Metric.TLabel',background='white',foreground=INK,font=('Arial',23,'bold'))
    style.configure('TButton',padding=(12,9),background='white',foreground=INK,bordercolor=BORDER,relief='flat')
    style.map('TButton',background=[('active','#eeebff'),('disabled','#f0f1f5')],foreground=[('disabled','#9399a8')])
    style.configure('Primary.TButton',background=ACCENT,foreground='white',bordercolor=ACCENT,font=('Arial',12,'bold'))
    style.map('Primary.TButton',background=[('active','#5142ba'),('disabled','#dedbea')],foreground=[('disabled','#9390a1'),('!disabled','white')])
    style.configure('TRadiobutton',background='white',padding=(10,9),font=('Arial',12))
    style.map('TRadiobutton',background=[('selected','#eeeafd'),('active','#f5f3ff')])
    style.configure('TCheckbutton',background=BG)
    style.configure('TCombobox',padding=6,fieldbackground='white',arrowsize=13)
    style.configure('Treeview',background='white',fieldbackground='white',rowheight=38,borderwidth=0,font=('Arial',11))
    style.configure('Treeview.Heading',background='#edf0f6',foreground=MUTED,padding=10,font=('Arial',11,'bold'),relief='flat')
    style.map('Treeview',background=[('selected','#e9e4ff')],foreground=[('selected',INK)])
    style.configure('TNotebook',background=BG,borderwidth=0)
    style.configure('TNotebook.Tab',padding=(18,10),background='#edf0f6',foreground=MUTED)
    style.map('TNotebook.Tab',background=[('selected','white')],foreground=[('selected',ACCENT)])
    style.layout('Shell.TNotebook.Tab',[])
    style.configure('Shell.TNotebook',borderwidth=0,background=BG)
    style.configure('Horizontal.TProgressbar',background=ACCENT,troughcolor='#eae7f9',borderwidth=0)
    return style


def rounded(canvas,x1,y1,x2,y2,r=12,**kwargs):
    points=[x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,x2-r,y2,
            x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
    return canvas.create_polygon(points,smooth=True,splinesteps=20,**kwargs)
