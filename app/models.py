from __future__ import annotations

from datetime import datetime
from enum import Enum, unique
from typing import Optional

from mb_commons import utc_now
from mb_commons.mongo import MongoModel, ObjectIdStr
from pydantic import BaseModel, Field, HttpUrl
from pymongo import IndexModel


@unique
class ProxyType(str, Enum):
    SOCKS5 = "SOCKS5"
    HTTP = "HTTP"


@unique
class ProxyStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    OK = "OK"
    DOWN = "DOWN"


class Group(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    name: str
    link: HttpUrl
    username: Optional[str] = None
    password: Optional[str] = None
    port: int
    type: ProxyType
    created_at: datetime = Field(default_factory=utc_now)
    checked_at: Optional[datetime]

    __collection__ = "group"
    __indexes__ = [
        IndexModel("name", unique=True),
        IndexModel("link", unique=True),
        IndexModel("created_at"),
        IndexModel("checked_at"),
    ]


class GroupCreate(BaseModel):
    name: str
    link: HttpUrl = None
    username: Optional[str] = None
    password: Optional[str] = None
    port: int
    type: ProxyType


class Proxy(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    group: str  # Group.name
    type: ProxyType
    status: ProxyStatus = ProxyStatus.UNKNOWN
    username: str
    password: str
    host: str
    port: int
    created_at: datetime = Field(default_factory=utc_now)
    checked_at: Optional[datetime]
    last_ok_at: Optional[datetime]

    __collection__ = "proxy"
    __indexes__ = [
        IndexModel("host", unique=True),
        IndexModel("group"),
        IndexModel("status"),
        IndexModel("type"),
        IndexModel("created_at"),
        IndexModel("checked_at"),
        IndexModel("last_ok_at"),
    ]

    @property
    def url(self):
        schema = "socks5" if self.type == ProxyType.SOCKS5 else "http"
        return f"{schema}://{self.username}:{self.password}@{self.host}:{self.port}"

    @classmethod
    def from_group(cls, group: Group, host: str) -> Proxy:
        return Proxy(
            group=group.name,
            type=group.type,
            username=group.username,
            password=group.password,
            host=host,
            port=group.port,
        )
