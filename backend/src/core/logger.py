"""
Logger - Log sistemi

Kullanım:
    from core.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("İşlem başladı")
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str,
    log_dir: Optional[str] = None,
    level: str = "INFO"
) -> logging.Logger:
    """
    Logger kurulumu
    
    Args:
        name: Logger adı (genelde __name__)
        log_dir: Log dosyasının kaydedileceği klasör
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Zaten handler varsa tekrar ekleme
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (eğer log_dir belirtilmişse)
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Günlük log dosyası
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_path / f"app_{today}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Logger al (hızlı erişim için)
    
    Args:
        name: Logger adı
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
