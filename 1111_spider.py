# 1111 人力銀行爬蟲 by Requests
import pandas as pd
import requests
import time
import random
import re
import datetime

class Job1111Spider():
    def search(self, keyword, max_num = 2, filter_params = None):
        """搜尋職缺"""
        jobs = ''
        job_list = []
        url = 'https://www.1111.com.tw/search/job?'
        query = f'ks={keyword}&act=load_page'

        if filter_params:
            query += ''.join([f'&{key}={value}' for key, value in filter_params.items()])

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                'Referer': 'https://www.1111.com.tw/'
            }
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                'Referer': 'https://www.1111.com.tw/'
            }

        page = 1
        while page <= max_num:
            params = f'{query}&page={page}'
            r = requests.get(url, params=params, headers=headers)
            if r.status_code != requests.codes.ok:
                print('請求失敗', r.status_code)
                break

            data = r.json()
            data = data['html1_d']

            """資料清理"""
            temp_text = re.sub('<div class="job_item_detail_salary ml-3 font-weight-style digit_6">', '\n; 薪資:', data)
            temp_text = re.sub('<div class="card-subtitle mb-4 text-muted happiness-hidd"><a href="', '\n; 公司連結:', temp_text)
            temp_text = re.sub('<a href="https://www.1111.com.tw/job', '\n\n|工作連結:https://www.1111.com.tw/job', temp_text)
            temp_text = re.sub('<p class="card-text job_item_description body_4">', '\n; 工作描述:\n', temp_text)
            temp_text = re.sub('<span class="item__job-desc-limit-item" data-b="" data-e="相關科系">', '\n; 相關科系:', temp_text)
            temp_text = re.sub('" title="', "\n", temp_text)
            temp_text = re.sub('《', "; ", temp_text)
            temp_text = re.sub('》', "：", temp_text)
            temp_text = re.sub('<h5 class="card-title title_6">', '\n; 工作名稱:', temp_text)
            temp_text = re.sub('; 品牌名稱.*',"",temp_text)
            temp_text = re.sub("'", '', temp_text)
            temp_text = re.sub('" target.*', "", temp_text)
            temp_text = re.sub('搜尋更多.*工作', "", temp_text)
            temp_text = re.sub('<em>', "", temp_text)
            temp_text = re.sub('</em>', "", temp_text)
            temp_text = re.sub('<.*', "", temp_text)
            temp_text = re.sub('[\n\r]', "", temp_text)  # 原本藉由 \n 的性質來消掉'<.{0,}>，在處理完之後再弄掉 \n
            jobs +=  temp_text

            page += 1
            time.sleep(random.uniform(3,5))

        """補值"""
        # 品牌名稱有問題
        job_list = jobs.split("|")
        for i in range(0, len(job_list)):
            if re.search("相關科系", job_list[i]) == None:
                job_list[i] += '; 相關科系: null'

        """製成 DataFrame"""
        df = pd.DataFrame(job_list)
        return df


if __name__ == "__main__":
    job1111_spider = Job1111Spider()

    filter_params = {
        # 'c0': '100100' # 地區
    }

    keyword = input('輸入關鍵字：')
    jobs = job1111_spider.search(f'{keyword}', max_num=10, filter_params=filter_params)
    print(jobs)


    # 匯入 excel
    # 存入excel

    filename = datetime.date.today() # 檔案名稱
    writer = pd.ExcelWriter(f'{filename}&{keyword}.xlsx')
    jobs.to_excel(writer, sheet_name='求職', index=False)
    writer.save()
