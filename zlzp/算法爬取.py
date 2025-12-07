import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from time import sleep
from selenium.common.exceptions import TimeoutException
import pandas as pd
from lxml import etree
import os
import random
import html as _html
import json


def main():
    """爬取职位数据"""
    resLs = []
    skipped = 0
    for p in range(pz):
        p += 1
        print(f'爬取第{p}页>>>')
        sleep(2)
        
        # 页面滚动加载内容
        for i in range(140):
            sleep(random.random() / 10)
            driver.execute_script('window.scrollBy(0, 50)')
        
        # 等待职位列表加载
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.j_joblist > div'))
            )
        except TimeoutException:
            print('等待超时，尝试额外滚动')
            for _ in range(3):
                driver.execute_script('window.scrollBy(0, 500)')
                sleep(1)
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.j_joblist > div'))
                )
            except TimeoutException:
                print('页面可能为空，继续采集')

        # 获取职位列表
        items = driver.find_elements(By.CSS_SELECTOR, '.joblist-item')
        if not items:
            try:
                os.makedirs('data', exist_ok=True)
                with open(f'data/{key}_last_page.html', 'w', encoding='utf-8') as _f:
                    _f.write(driver.page_source)
                print(f'未找到职位，页面已保存至 data/{key}_last_page.html')
            except Exception as _e:
                print('保存页面失败：', _e)
        
        for it in items:
            try:
                # 获取职位基本信息
                job_elem = None
                try:
                    job_elem = it.find_element(By.CSS_SELECTOR, '.joblist-item-job')
                except Exception:
                    job_elem = None

                sensors = None
                if job_elem:
                    try:
                        sensors = job_elem.get_attribute('sensorsdata') or job_elem.get_attribute('sensordata')
                    except Exception:
                        sensors = None

                if sensors:
                    try:
                        info = json.loads(_html.unescape(sensors))
                        job_title = info.get('jobTitle', '')
                        job_salary = info.get('jobSalary', '')
                        job_area = info.get('jobArea', '')
                        job_year = info.get('jobYear', '')
                        job_degree = info.get('jobDegree', '')
                    except Exception as e:
                        print('解析属性失败，使用DOM文本：', e)
                        sensors = None

                # 回退到DOM文本提取
                if not sensors:
                    def safe_text(elem, selectors):
                        for sel in selectors:
                            try:
                                el = elem.find_element(By.CSS_SELECTOR, sel)
                                txt = el.text.strip()
                                if txt:
                                    return txt
                            except Exception:
                                continue
                        return ''

                    job_title = safe_text(it, ['.jname', '.jname.text-cut', '.job-title', '.jobname'])
                    job_salary = safe_text(it, ['.sal', '.sal.shrink-0', '.salary'])
                    job_area = safe_text(it, ['.area .shrink-0', '.joblist-item-bot .area .shrink-0', '.joblist-item-mid .area'])
                    extra = safe_text(it, ['.joblist-item-job .tag-list', '.joblist-item-job'])
                    job_year = ''
                    job_degree = ''
                    if extra:
                        parts = [p.strip() for p in extra.replace('/', ' ').replace('·', ' ').split() if p.strip()]
                        for p in parts:
                            if any(ch.isdigit() for ch in p) and ('年' in p or '经验' in p):
                                job_year = p
                            if p.endswith('及以上') or p in ('本科', '大专', '硕士', '博士') or '学历' in p:
                                job_degree = p

                # 获取公司信息
                try:
                    c_name = it.find_element(By.CSS_SELECTOR, '.cname').text.strip()
                except Exception:
                    c_name = safe_text(it, ['.cname', '.cname.text-cut'])

                # 公司额外字段（行业、性质、规模等）
                c_fields = []
                try:
                    for el in it.find_elements(By.CSS_SELECTOR, '.dc'):
                        txt = el.text.strip()
                        if txt:
                            c_fields.append(txt)
                except Exception:
                    pass

                c_field_0 = c_fields[0] if len(c_fields) > 0 else ''
                c_field_1 = c_fields[1] if len(c_fields) > 1 else ''
                c_num = c_fields[2] if len(c_fields) > 2 else '未知'

                dit = {
                    '职位': job_title,
                    '薪资': job_salary,
                    '城市': job_area,
                    '经验': job_year,
                    '学历': job_degree,
                    '公司': c_name,
                    '公司领域': c_field_0,
                    '公司性质': c_field_1,
                    '公司规模': c_num
                }
                if not job_title:
                    skipped += 1
                    continue

                print(dit)
                resLs.append(dit)
            except Exception as e:
                skipped += 1
                print('解析失败：', e)

        # 翻页
        if p != pz:
            try:
                driver.find_element(By.ID, 'jump_page').clear()
                driver.find_element(By.ID, 'jump_page').send_keys(p + 1)
                sleep(random.random())
                driver.find_element(By.CLASS_NAME, 'jumpPage').click()
            except Exception as e:
                print('翻页失败：', e)

    # 保存为CSV
    print(f'爬取完成：共 {len(resLs)} 条，跳过 {skipped} 条')
    if resLs:
        os.makedirs('data', exist_ok=True)
        pd.DataFrame(resLs).to_csv(f'data/{key}.csv', index=False, encoding='utf-8-sig')
        print(f'已保存至 data/{key}.csv')
    else:
        print('未获取到数据')


if __name__ == '__main__':
    pz = 20  # 爬取页数
    for key in ['金融', '财务']:
        options = ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(options=options)
        
        # 使用selenium-stealth降低被检测风险
        stealth_used = False
        try:
            import importlib
            stealth_mod = importlib.import_module('selenium_stealth')
            stealth = getattr(stealth_mod, 'stealth', None)
            if stealth:
                try:
                    stealth(driver,
                            user_agent=None,
                            languages=["zh-CN", "zh"],
                            vendor="Google Inc.",
                            platform="Win32",
                            webgl_vendor="Intel Inc.",
                            renderer="ANGLE (Intel(R) Iris(TM) Graphics, OpenGL 4.1)",
                            fix_hairline=True)
                    stealth_used = True
                    print('已启用 selenium_stealth')
                except Exception as e:
                    print('启用 stealth 失败：', e)
        except Exception:
            pass

        # 备用方案：从本地stealth.min.js注入
        if not stealth_used:
            js = None
            try:
                with open('stealth.min.js', 'r', encoding='utf-8') as _fj:
                    js = _fj.read()
            except FileNotFoundError:
                print("未找到 stealth.min.js")
            except Exception as e:
                print('读取 stealth.min.js 失败：', e)

            if js:
                try:
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
                    print('已注入 stealth 脚本')
                except Exception as e:
                    print('注入脚本失败：', e)
        
        driver.get(f'https://we.51job.com/pc/search?keyword={key}&searchType=2&sortType=0&metro=')
        sleep(2)
        main()
        driver.quit()

# =================================
# 数据清洗与入库
# =================================

DO_DB_INSERT = False  # 是否写入MongoDB

import pymongo
import pandas as pd


def clearSalary(string):
    """清洗薪资字符串，转换为月薪数值"""
    try:
        firstNum = string.split('-')[0]
        firstNum = eval(firstNum.strip('千万'))
        if '千' in string:
            num = firstNum * 1000
        elif '万' in string:
            num = firstNum * 10000
        if '年' in string:
            num /= 12
        return num
    except:
        return None


def clear(df):
    """清洗数据：转换薪资、移除重复、移除缺失值"""
    df['薪资'] = df['薪资'].apply(clearSalary)
    df.duplicated(keep='first')
    df.dropna(how='any', inplace=True)
    return df


def insert():
    """从CSV读取并写入MongoDB"""
    df = pd.read_csv(f'data/{key}.csv', encoding='utf-8-sig')
    df = clear(df)
    resLs = df.to_dict(orient='records')
    for res in resLs:
        res['key'] = key
        collection.insert_one(res)
        print(res)


if __name__ == '__main__':
    client = pymongo.MongoClient('mongodb://root:abc_123456@localhost:27017')
    db = client.test
    collection = db.job
    if DO_DB_INSERT:
        for key in ['金融', '财务']:
            insert()
    else:
        print('DO_DB_INSERT = False，跳过MongoDB写入')