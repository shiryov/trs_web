# -*- coding: utf8 -*-
from django.db import models
import custom_fields
import datetime
#import mptt

# Create your models here.
class Message(models.Model):
    user = models.ForeignKey('User')
    time = models.DateTimeField(auto_now=True,auto_now_add=True)
    text = models.TextField()
    #true если это ответ поддержки
    reply = models.BooleanField(default=False)
    ticket = models.ForeignKey('Ticket')
    ip = models.IPAddressField(blank=True,null=True)
    

class User(models.Model):
    name = models.CharField("Имя",max_length=60)
    email = models.EmailField(blank=True,null=True)
    phone = models.CharField("Внутр. телефон",max_length=30,blank=True,null=True)
    mobile = models.CharField("Корп. мобильный",max_length=30,blank=True,null=True)
    city_phone = models.CharField("Городской телефон",max_length=30,blank=True,null=True)
    sat_phone = models.CharField("Спутниковый телефон",max_length=30,blank=True,null=True)
    personal_phone = models.CharField("Личный телефон",max_length=30,blank=True,null=True)
    admin = models.BooleanField(default=False)
    login = models.CharField(max_length=16,blank=True,null=True)
    password = models.CharField(max_length=32,blank=True,null=True)
    place = models.ForeignKey('Place',blank=True,null=True)

class Device(models.Model):
    TYPE_CHOICES=(
        ('00','Компьютер'),
        ('10','Монитор'),
        ('20','Принтер'),
        ('30','МФУ'),
        ('40','Плоттер'),
        ('50','Сканер'),
        ('60','Сервер'),
        ('70','Маршрутизатор'),
        ('80','Модем'),
    )
    type=models.CharField(max_length=3,choices=TYPE_CHOICES)
    inv_no=models.CharField(max_length=40)
    ip=models.IPAddressField(blank=True,null=True)
    model=models.CharField(max_length=60,blank=True,null=True)
    mac=custom_fields.MACAddressField(blank=True,null=True)
    info=models.TextField(blank=True,null=True)
    place = models.ForeignKey('Place')
    hostname=models.CharField(blank=True,null=True,max_length=40)
    def type_display(self):        
        for desc in self.TYPE_CHOICES:
            if desc[0]==self.type:
                return desc[1]
    def get_absolute_url(self):
        return "/place/"+str(self.place.id)

class Ticket(models.Model):
    #NEW,OPEN,CLOSED,DELETED
    STATUS_CHOICES=(
        ('00','Новое'),
        ('10','Принято'),
        ('20','Ожидаем ответ'),
        ('30','Закрыто'),
        ('40','Удалено'),        
    )
    PRIO_CHOICES=(
        ('00','Крайне срочно'),
        ('10','Срочно'),
        ('20','Обычно'),
        ('30','Длительное')
    )

    CATEGORY_CHOICES=(
        ('00','Компьютеры, локальный софт, железо'),
        ('10','Печать, принтеры, расходники'),
        ('20','Корпоративные системы (SAP,АСУД ..)'),
        ('30','Сетевые сервисы и оборуд., Серверы'),
        ('40','СКС (провода, розетки)'),
    
    )

    status = models.CharField("Статус",max_length=3, choices=STATUS_CHOICES)
    priority = models.CharField("Приоритет",max_length=3, choices=PRIO_CHOICES)
    category = models.CharField("Категория",max_length=3, choices=CATEGORY_CHOICES,blank=True,null=True)
    hours_limit=models.DecimalField("Лимит времени, ч.",max_digits=4, decimal_places=1,default=2)
    #Описание проблемы. при создании тикета - присваиваем текст 1го обращения
    #В процессе выполнения заявки можем менять
    description = models.TextField("Описание проблемы")
    #Описание решения по закрытии заявки
    resume = models.TextField("Отчёт о решении",blank=True,null=True)
    user = models.ForeignKey(User,related_name="tickets")
    admin = models.ForeignKey(User,related_name="tasks",blank=True,null=True)
    device = models.ForeignKey(Device,blank=True,null=True)    
    #Время создания. 
    ctime = models.DateTimeField(auto_now_add = True)
    #Время закрытия
    closing_time = models.DateTimeField(blank=True,null=True)

    def get_short_text(self):
        return self.description[:120]
    
    def hours_from_now(self):
        delta=datetime.datetime.now()-self.ctime
        return round(delta.days*24.0+delta.seconds/3600.0,1)

    def is_new(self,*args):
        value=self.status
        if args:
            value=args[0]
        if value=='00':
            return True
        else:
            return False

    def is_closed(self,*args):
        value=self.status
        if args:
            value=args[0]
        if value=='30':
            return True
        else:
            return False
        
    def accept_by(self,user):
        self.admin=user
        
    def no(self):
        return '{0:0>5}'.format(self.id)
        
class Place(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey('self',null=True, blank=True )
    address = models.CharField(max_length=70)
    LEVEL_DESC=(
    (1,"Населённый пункт"),
    (2,"Территория, группа зданий"),
    (3,"Здание"),
    (4,"Этаж"),
    (5,"Кабинет/помещение"),
    (6,"Место/комплекс"),
    )
    def childs(self):
        return Place.objects.filter(parent=self)
    
    def get_level(self):
        res=0
        try:
            if self.parent!=None:
                o=self
                while (o.parent !=None):
                    res+=1
                    o=o.parent
        except:
            None
        return res
    
    def level_display(self):
        level=self.get_level()
        for desc in self.LEVEL_DESC:
            if desc[0]==level:
                return desc[1]
    
    def path(self):        
        path=[]
        o=self
        while (o.parent != None):
            path.insert(0,o)
            o=o.parent
        path.insert(0,o)
        return path
    def get_absolute_url(self):
        return '/place/'+str(self.id)
    def __unicode__(self):
        return self.name
    
    def users(self):
        return User.objects.filter(place=self)

#mptt.register(Place)

class Document(models.Model):
    name=models.CharField(max_length=60)
    place=models.ForeignKey(Place,blank=True,null=True)
    def latest_file(self):
        return DocFile.objects.filter(document=self).order_by('-id')[0]
    
class DocFile(models.Model):
    document=models.ForeignKey(Document)
    version=models.IntegerField()
    file_name=models.CharField(max_length=60)
    comment=models.CharField(max_length=90,blank=True,null=True)
    ctime = models.DateTimeField()
    user = models.ForeignKey(User)
    
