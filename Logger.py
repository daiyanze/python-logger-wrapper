# -*- coding: utf-8 -*-

' a logging module '

__author__ = 'Yanze Dai'

import logging, traceback
from datetime import date
from functools import wraps
from logging.handlers import RotatingFileHandler
from inspect import getframeinfo, trace

_print_format = '%(name)-6s: %(levelname)-6s %(message)s'
_rotate_format = '%(asctime)s (%(levelname)s) %(message)s'
_log_file = 'log/' + str(date.today())
_logger_name = 'Your Log'
_is_debug = True

class Logger:
	"""
	[summary] Generate logs for each program operations
	
	Attributes:
		log_file {string} -- log file name
		logger_name {string} -- name for this logger
		debug {bool} -- debug mode True/False. Once True, DEBUG level info will be logged down and info will be
			printed out on terminal screen.
	"""

	def __init__(self, log_file, logger_name=_logger_name, *, debug=_is_debug):
		self.log_file = log_file
		self.logger_name = logger_name
		self.debug = debug

	def getLog(self):
		"""
		[summary] Get instance of logging object

		Returns:
			{logging object} -- instance of logging object
		"""
		self.logger = logging.getLogger(self.logger_name)
		self.logger.setLevel(self._level())
		self.logger.addHandler(self._rotateLog())
		if self.debug is True:
			self.logger.addHandler(self._printLog())
		return self.logger

	def _printLog(self):
		"""
		[summary] Print out log on terminal

		Returns:
			{StreamHandler object} sh -- instance of StreamHandler object
		"""
		sh = logging.StreamHandler()
		sh.setLevel(self._level())
		formatter = logging.Formatter(_print_format)
		sh.setFormatter(formatter)
		return sh

	def _rotateLog(self):
		"""
		[summary] Rotate new log if log exceeds limited size

		Returns:
			{RotatingFileHandler object} sh -- instance of RotatingFileHandler object
		"""
		rh = RotatingFileHandler(self.log_file, maxBytes=10*1024*1024, backupCount=5)
		rh.setLevel(self._level())
		formatter = logging.Formatter(_rotate_format)
		rh.setFormatter(formatter)
		return rh

	def _level(self):
		"""
		[summary] Set log level

		Returns:
			{logging object} -- instance of logging object
		"""
		return self.debug and logging.DEBUG or logging.INFO

logger = Logger(_log_file, _logger_name).getLog()

def log(argument, *, level='info'):
	"""
	[summary] Create a decorator by wrapping function
	
	Decorators:
		wraps (from functools.wraps)
	
	Arguments:
		argument {string} -- Something for logging
	
	Keyword Arguments:
		level {str} -- Log level/type (default: {'info'})
	
	Returns:
		decorator/wrapper -- wrapper function
	"""
	if callable(argument):
		def wrapper(*args, **kwargs):
			try:
				return argument(*args, **kwargs)
			except Exception as e:
				caller = getframeinfo(trace()[1][0])
				logger.error("%s:%d - %s" % (caller.filename, caller.lineno, e), exc_info=traceback.format_exc())
		return wrapper
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			try:
				try:
					logger.__getattribute__(level)(argument)
				except AttributeError:
					logger.info(argument)
				return func(*args, **kwargs)
			except Exception as e:
				caller = getframeinfo(trace()[1][0])
				logger.error("%s:%d - %s" % (caller.filename, caller.lineno, e), exc_info=traceback.format_exc())
		return wrapper
	return decorator
