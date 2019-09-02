from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import TimeoutException

class Delete:

	def __init__(self):
		self.__u = ''
		self.__p = ''#注意个人信息
		self.__driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver')

	# 登录qq空间
	def login(self):
		# driver.get 方法会打开请求的URL，WebDriver 会等待页面完全加载完成之后才会返回，
		# 即程序会等待页面的所有内容加载完成，JS渲染完毕之后才继续往下执行。
		# 注意：如果这里用到了特别多的 Ajax 的话，程序可能不知道是否已经完全加载完毕。
		self.__driver.get("https://qzone.qq.com")
		self.__driver.switch_to.frame('login_frame')
		self.__driver.find_element_by_id('switcher_plogin').click()
		self.__driver.find_element_by_id('u').send_keys(self.__u)
		self.__driver.find_element_by_id('p').send_keys(self.__p)
		self.__driver.find_element_by_id('login_button').click()
		# 从frame返回
		self.__driver.switch_to.default_content()

	def switch2board(self):
		# 找到留言板按钮
		WebDriverWait(self.__driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//a[@title="留言板"]'))
		).click()

		# 黄钻过期提醒
		# WebDriverWait(self.__driver, 10).until(
		# 	EC.presence_of_element_located((By.ID, "dialog_button_1"))
		# ).click()

		# 确保留言板所在的frame已经加载完并切换
		WebDriverWait(self.__driver, 10).until(
			EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@id="tgb"]'))
		)

	def getTotalPage(self):
		# 页数为一页的时候没有a标签
		try:
			# 为什么
			# totalPage = driver.find_element_by_xpath('//span[@class="mod_pagenav_count"]/a[last()]').text
			# 为什么输出为空，text属性不是文本内容？？ 还是说是谷歌浏览器的问题？？
			return int(self.__driver.find_element_by_xpath('//span[@class="mod_pagenav_count"]/a[last()]')
						.get_attribute('innerHTML'))
		except EC.NoSuchElementException:
			return 1

	# 点击确定删除按钮，并回到留言板的frame
	def handlePopWin(self, selectedItem=None):
		# 弹窗不在frame中
		self.__driver.switch_to.default_content()
		try:
            
			WebDriverWait(self.__driver, 3).until(
        			EC.presence_of_element_located((By.XPATH, '//a[@class="qz_dialog_layer_btn qz_dialog_layer_sub"]'))
        		).click()
		except TimeoutException as e: #由于QQ空间bug，多选删除完多个留言后，无法再继续勾选删除，上面语句会出现超时错误
			self.__driver.refresh()   #刷新页面，重新执行操作
			self.switch2board()
			self.deleteByNum(num)
            
		if selectedItem:
			print('删除 %d 条记录' % selectedItem)
		else:
			print('删除一页记录')

		# 确保留言板所在的frame已经加载完并切换
		WebDriverWait(self.__driver, 3).until(
			EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@id="tgb"]'))
		)

	# 删除所有的留言
	def deleteAll(self):
		# totalPage = self.getTotalPage()

		# # 留言板设置的sub_lsit
		# WebDriverWait(driver, 10).until(
		# 	EC.presence_of_element_located((By.XPATH, '//ul[@class="sub_list bg bor"]'))
		# )
		# # getElementsByClassName返回的是集合
		# driver.execute_script('document.getElementsByClassName("sub_list bg bor")[0].style.display="block"')
		# # 进入批量管理
		# driver.find_element_by_id('btnBatch').click()

		for i in range(self.getTotalPage()):
			time.sleep(3)
			# 执行js语句可以直接设置id=divBatchOper元素的可见性来进入批量管理
			self.__driver.execute_script('document.getElementById("divBatchOper").style.display="block"')
			self.__driver.find_element_by_id('chkSelectAll').click()
			self.__driver.find_element_by_id('btnDeleteBatchBottom').click()
			self.handlePopWin()

	# 删除指定qq的留言
	def deleteByNum(self, num):
		# 显示批量管理
		self.__driver.execute_script('document.getElementsByClassName("sub_list bg bor")[0].style.display="block"')
		time.sleep(3)
		self.__driver.find_element_by_id('btnBatch').click()
		while True:
			time.sleep(3)
			selectedItem = 0
			# 找到该页中所有的留言
			for li in self.__driver.find_elements_by_xpath('//li[@class="bor3"]'):
				# 如果输入的qq号在标签内，说明是该qq的留言，选中该条留言
				if num in li.get_attribute('innerHTML'):
					li.find_element_by_class_name('item_check_box').click()
					selectedItem += 1

			# 滚动到顶部
			self.__driver.execute_script('parent.scrollTo(0,200)')
			# 该页中确实有目标qq的留言才进行删除
			if selectedItem != 0:
				# 点击 删除选中的 按钮
				self.__driver.find_element_by_id('btnDeleteBatchBottom').click()
				self.handlePopWin(selectedItem)
			# 该页中没有目标qq的留言处理下一页
			else:
				nextBtn = WebDriverWait(self.__driver, 3).until(
					EC.presence_of_element_located((By.XPATH, '//div[@id="pager_top"]//p[@class="mod_pagenav_main"]/a[last()]'))
				)
				# print(nextBtn.get_attribute('class'))
				# nextBtn = self.__driver.find_element_by_xpath('//div[@id="pager_top"]//p[@class="mod_pagenav_main"]/a[last()]')
				# 还有下一页
				if nextBtn.get_attribute('class') == 'c_tx' or nextBtn.get_attribute('class') == 'c_tx ':
					print('切换到下一页！')
					nextBtn.click()
				elif nextBtn.get_attribute('class') == 'c_tx none':
					return

	def start(self, num=None):
		self.login()
		self.switch2board()
		if num:
			self.deleteByNum(num)
		else:
			self.deleteAll()
		print('删除完成')
		self.__driver.quit()

if __name__ == '__main__':
		# delete = Delete()
		# delete.start()
	num = '670872031'
	delete = Delete()
	delete.start(num = num)
