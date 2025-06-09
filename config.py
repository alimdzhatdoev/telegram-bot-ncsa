from dataclasses import dataclass, field

@dataclass
class Config:
    bot_token: str = '7944416596:AAFJrVR8sUwSwudbhz9F9sjKPYGj1Qvssjk'
    admin_ids: list[int] = field(default_factory=lambda: [992109845, 1451874173])

config = Config()
