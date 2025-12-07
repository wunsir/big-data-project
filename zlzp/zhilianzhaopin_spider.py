import time
import csv
import os
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_target_info_selenium(driver, results):
    """从网页中提取职位和公司信息"""
    try:
        # 等待职位列表加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "positionlist"))
        )
        job_items = driver.find_elements(By.CSS_SELECTOR, ".joblist-box__item")
        for job_item in job_items:
            try:
                job_name = job_item.find_element(By.CSS_SELECTOR, ".jobinfo__name").text.strip()
                company_name = job_item.find_element(By.CSS_SELECTOR, ".companyinfo__name").text.strip()
                salary = job_item.find_element(By.CSS_SELECTOR, ".jobinfo__salary").text.strip()

                # 提取工作地点、经验、学历
                try:
                    job_info_elements = job_item.find_elements(By.CSS_SELECTOR, ".jobinfo__other-info-item")
                    location = job_info_elements[0].text.strip() if len(job_info_elements) >= 1 else ""
                    experience = job_info_elements[1].text.strip() if len(job_info_elements) >= 2 else ""
                    education = job_info_elements[2].text.strip() if len(job_info_elements) >= 3 else ""
                    job_requirement = f"{experience},{education}"
                except Exception as e:
                    print(f"获取岗位要求出错:{e}")
                    job_requirement = "暂无"
                    location = "暂无"

                # 提取职位技能标签
                requirement_tags = []
                try:
                    tag_elements = job_item.find_elements(
                        By.CSS_SELECTOR,
                        'div.jobinfo__tag .joblist-box__item-tag'
                    )
                    requirement_tags = [tag.text.strip() for tag in tag_elements]
                except Exception as e:
                    print(f"获取职位要求出错:{e}")

                requirement = ",".join(requirement_tags) if requirement_tags else "暂无"

                # 提取公司标签
                company_tags = []
                try:
                    tag_elements = job_item.find_elements(
                        By.CSS_SELECTOR,
                        'div.companyinfo__tag .joblist-box__item-tag'
                    )
                    company_tags = [tag.text.strip() for tag in tag_elements]
                except Exception as e:
                    print(f"获取公司信息出错:{e}")

                ct = ",".join(company_tags) if company_tags else "暂无"
                results.append([job_name, company_name, salary, job_requirement, location, requirement, ct])
            except Exception as e:
                print(f"解析职位出错:{e}")
                continue
    except Exception as e:
        print(f"获取职位列表出错:{e}")


def write2file(current_page, results, fileType, savePath):
    """保存爬取结果到文件"""
    save_dir = r'C:\Users\czwxr\Desktop\DSAI\zhaopin_data'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if fileType.endswith(".xlsx") or fileType.endswith(".xls"):
        file_path = os.path.join(save_dir, 'zhilianzhaopin_python.xlsx')
        df = pd.DataFrame(results[1:], columns=results[0])

        if current_page == 1:
            df.to_excel(file_path, index=False, engine='openpyxl')
        else:
            existing_df = pd.read_excel(file_path, engine='openpyxl')
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.to_excel(file_path, index=False, engine='openpyxl')

        print(f'第{current_page}页数据已保存')

    elif fileType.endswith(".csv"):
        save_dir_csv = os.path.join(savePath, 'to_csv')
        if not os.path.exists(save_dir_csv):
            os.makedirs(save_dir_csv)

        file_path = os.path.join(save_dir_csv, 'zhilianzhaopin_python.csv')

        if current_page == 1:
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as wf:
                writer = csv.writer(wf)
                writer.writerow(['岗位名称', '公司名称', '岗位薪资', '岗位要求', '公司位置', '技术要求', '企业信息'])

        with open(file_path, 'a', encoding='utf-8-sig', newline='') as af:
            writer = csv.writer(af)
            for row in results[1:]:
                writer.writerow(row)

        print(f'第{current_page}页数据已保存')



def process_zhilianzhaopin_selenium(baseUrl, pages, fileType, savePath):
    """爬取智联招聘职位数据"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        results = [['岗位名称', '公司名称', '岗位薪资', '岗位要求', '公司位置', '技术要求', '企业信息']]

        for page in range(1, int(pages) + 1):
            url = baseUrl + str(page)
            print(f"爬取第{page}页...")
            driver.get(url)
            time.sleep(3)
            
            get_target_info_selenium(driver, results)
            write2file(page, results, fileType, savePath)
            # 重置结果列表（保留表头）
            results = [['岗位名称', '公司名称', '岗位薪资', '岗位要求', '公司位置', '技术要求', '企业信息']]
            
            delay = random.randint(3, 7)
            time.sleep(delay)

        print(f'共爬取{page}页，完成')

    except Exception as e:
        print(f"爬取出错:{e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    base_url = "https://sou.zhaopin.com/?jl=765&kw=财务&p="
    save_path = "zhilian_spider"
    page_total = "30"
    process_zhilianzhaopin_selenium(base_url, page_total, ".xlsx", save_path)
