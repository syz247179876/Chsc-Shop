# -*- coding: utf-8 -*-
# @Time  : 2020/8/16 下午4:33
# @Author : 司云中
# @File : storage.py
# @Software: Pycharm
import oss2 as oss2
from django.core.files import File
from django.core.files.storage import Storage
from django.conf import settings
from Emall.loggings import Logging
from Emall.settings import FDFS_URL, FDFS_CLIENT_CONF
from django.utils.deconstruct import deconstructible

from fdfs_client.client import Fdfs_client, get_tracker_conf

common_logger = Logging.logger('django')


@deconstructible
class FastDfsStorage(Storage):
    """操作文件通过file_id"""

    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url:构造图片上传的基本url，包括域名，已经搭配nginx
        :param client_conf:FastDfs客户端的配置字典
        """
        if base_url is None:
            base_url = FDFS_URL
        self.base_url = base_url
        if client_conf is None:
            client_conf = FDFS_CLIENT_CONF
        self.client_conf = client_conf
        self.client = Fdfs_client(get_tracker_conf(self.client_conf))

    def _open(self, name, mode='rb'):
        """返回封装后的文件对象"""
        return File(open(self.path(name), mode))

    def open(self, name, mode='rb'):
        """
        从FastDfs中取出文件
        :param name: 文件名
        :param mode: 打开的模式
        :return:
        """
        return self._open(name, mode)

    def _save(self, name, content):
        """
        存储文件到FastDfs上
        :param name:  文件名（无卵用)
        :param content: 打开的file对象
        :return:
        """
        filebuffer = content.read()  # 读取二进制内容
        is_save, ret_upload = self.upload(filebuffer)
        return ret_upload.get('Remote file_id').decode() if is_save else None

    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        # 要不要name无所谓，只是为了尽量不改底层源码
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        name = self.get_available_name(name, max_length=max_length)  # 截取固定大小的文件名长度
        return self._save(name, content)

    def update(self, filebuffer, remote_file_id):
        """
        修改文件内容
        :param local_path: 本地文件名
        :param remote_file_id:  fastdfs中的file_id
        @return: dictionary {
            'Status'     : 'Modify successed.',
            'Storage IP' : storage_ip
        }
        """

        try:
            remote_file_id = bytes(remote_file_id.encode("utf-8"))  # 旧的file_id
            ret_update = self.client.modify_by_buffer(filebuffer, remote_file_id)
            if ret_update.get("Status") != 'Modify successed.':
                raise Exception
            return True, ret_update
        except Exception as e:
            common_logger.info(e)
            return None, "文件更新失败"

    def upload(self, filebuffer, meta_dict=None):
        """
        保存文件时回调的函数
        保存在FastDfs中
        通过client来操作
        :param name: 文件名
        :param filebuffer: 文件内容（二进制）
        :param meta_dict: dictionary e.g.:{
            'ext_name'  : 'jpg',
            'file_size' : '10240B',
            'width'     : '160px',
            'hight'     : '80px'
        }
        @return dict {
            'Group name'      : group_name,
            'Remote file_id'  : remote_file_id,
            'Status'          : 'Upload successed.',
            'Local file name' : '',
            'Uploaded size'   : upload_size,
            'Storage IP'      : storage_ip
        } if success else None
        """
        try:
            ret_upload = self.client.upload_by_buffer(filebuffer)
            if ret_upload.get("Status") != "Upload successed.":
                raise Exception
            return True, ret_upload
            # file_name为bytes类型，只能返回str类型，不然会报错
        except Exception as e:
            return False, None

    def url(self, name):
        """
        返回文件的完整URL路径给前端
        :param name: 数据库中保存的文件名
        :return: 完整的URL
        """
        return self.base_url + '/' + name

    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件的重名问题
        所以此处返回False，告诉Django上传的都是新文件
        :param name:  文件名
        :return: False
        """
        return False

    def download_to_file(self, local_path, remote_file_id):
        """
        从FastDfs分布式文件系统进行下载文件,保存成文件格式
        :param local_path: 本地保存文件路径
        :param remote_file_id: 上传到FastDfs文件系统中自动生成的文件路径即文件id,
        :return True/False, dict {
            'Remote file_id'  : remote_file_id,
            'Content'         : local_filename,
            'Download size'   : downloaded_size,
            'Storage IP'      : storage_ip
        }
        """
        try:
            ret_download = self.client.download_to_file(local_path, remote_file_id)
            return True, ret_download
        except Exception as e:
            return False, None

    def download_to_buffer(self, remote_file_id, offset=0, down_bytes=0):
        """
        通过文件名从FastDfs上下载文件,存储为buffer格式
        :param local_filename: 本地文件名，一般存于数据库
        :param remote_file_id: 远程文件id
        :param offset: 文件数据起始偏移量
        :param down_bytes: 需要下载的文件大小
        :return:return True/False, dict {
            'Remote file_id'  : remote_file_id,
            'Content'         : file_buffer,
            'Download size'   : downloaded_size,
            'Storage IP'      : storage_ip
        }
        """
        try:
            ret_download = self.client.download_to_buffer(remote_file_id, offset, down_bytes)
            return True, ret_download
        except Exception as e:
            return False, None

    def modify_by_buffer(self, filebuffer, appender_fileid, offset=0):
        """
        通过buffer修改文件内容
        :param filebuffer:文件buffer
        :param appender_fileid:远程文件id
        :param offset:起始偏移量
        :return:True/False, dictionary {
            'Status'     : 'Modify successed.',
            'Storage IP' : storage_ip
        }
        """

        try:
            ret_modify = self.client.modify_by_buffer(filebuffer, appender_fileid, offset)
            return True, ret_modify
        except Exception as e:
            return False, None

    def delete(self, remote_file_id):
        """
        从FastDfs分布式文件系统中将文件删除
        :param remote_file_id: 上传到FastDfs文件系统中自动生成的文件路径即文件id
        @return True/False, tuple ('Delete file successed.', remote_file_id, storage_ip)
        """
        try:
            ret_delete = self.client.delete_file(remote_file_id)
            return True, ret_delete
        except Exception as e:
            return False, None

class OSS(object):
    """操作OSS对象存储,上传文件"""

    def __init__(self, app=None, config=None):
        self.config = config
        self.bucket = None
        self.auth = None
        self.base_url = None
        self.set_auth()
        self.set_bucket()
        self.set_base_url()

    def set_auth(self):
        """设置认证信息"""
        access_key_id = settings.ACCESS_KEY_ID
        access_key_secret = settings.ACCESS_KEY_SECRET
        self.auth = oss2.Auth(access_key_id, access_key_secret)

    def set_bucket(self):
        """设置oss图床"""

        oss_bucket_name = settings.OSS_BUCKET_NAME
        endpoint = settings.OSS_ENDPOINT
        self.bucket = oss2.Bucket(self.auth, endpoint, oss_bucket_name)

    def set_base_url(self):
        """
        获取返回的基本路由,用于提供用户访问数据地址
        或者是存数数据库的字段值
        """
        self.base_url = settings.OSS_BASE_URL

    def upload_file(self, file, folder):
        """
        上传目标文件
        :param file werkzeug.datastructures.FileStorage 对象
        :param folder 文件夹
        :return 用户访问的路径 / 上传异常
        """
        filename = self.filename(file)
        related_path = self.file_related_path(filename, folder)
        outer_net = self.outer_net(related_path)
        is_existed = self.bucket.object_exists(related_path)

        if is_existed:  # 文件已经存在, 可以无需此功能
            raise FileExistedException()
        try:
            result = self.bucket.put_object(related_path, self.get_buffer(file))
            if result.status == 200:
                return outer_net
        except NoSuchBucket:
            raise UploadFileOSSError()
        except InvalidArgument:
            raise UploadFileOSSError()

    def delete_file(self, file, folder=None):
        """
        从oss的bucket中删除一个文件
        :param file: 文件
        :param folder:
        :return: True / raise
        """
        folder = folder if folder else ''
        filename = self.filename(file)
        related_path = self.file_related_path(filename, folder)
        result = self.bucket.delete_object(related_path)
        if result.status == 200:
            return True
        raise DeleteFileOSSError()

    def outer_net(self, file_related_path):
        """
        生成外网访问路径
        :param file_related_path:  文件相对bucket的路径
        :return: absolute path of file
        """
        return os.path.join(self.base_url, file_related_path)

    @staticmethod
    def file_related_path(filename, folder=None):
        """
        生成文件相对路径
        :param filename: 文件名
        :param folder: 文件夹
        :return:
        """
        folder = folder if folder else ''
        return os.path.join(folder, filename.replace('\\', '/'))

    @staticmethod
    def filename(file):
        """
        获取文件名
        :param file:FileStorage文件对象
        :return: 文件名
        """
        return file.filename

    @staticmethod
    def get_buffer(file):
        """
        获取文件二进制内容
        :param file:FileStorage文件对象
        :return: buffer
        """
        return file.stream.read()

