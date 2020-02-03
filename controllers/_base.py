import hashlib
import uuid
import jwt
import requests

from abc import ABC
from urllib.parse import urlencode


class RequestController(ABC):
    """최상위 요청 컨트롤러"""

    def __init__(self, query=None):
        self.__request_url = 'https://api.upbit.com'
        self.__query = query
        self.__headers = {}

    @property
    def request_url(self):
        return self.__request_url

    @request_url.setter
    def request_url(self, sub_url):
        """요청 주소 설정"""
        self.__request_url = self.request_url + sub_url

    def set_headers(self, access_key, secret_key, params=None):
        """인증된 요청을 위한 헤더 설정"""
        # 요청 페이로드 생성
        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
        }

        # 파라미터가 있는 경우 파라미터를 담아서 payload 업데이트
        if params:
            hash_type = hashlib.sha512()
            hash_type.update(urlencode(params).encode())
            hashed_params = hash_type.hexdigest()
            payload.update({
                'query_hash': hashed_params,
                'query_hash_alg': 'SHA512'
            })

        # 인증 토큰 생성 후 요청 헤더 설정
        jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
        self.__headers.update({
            'Authorization': 'Bearer {}'.format(jwt_token)
        })
