import os, requests
import urllib.parse


demo_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}


def download_file(url, filename=None):

    download_dir = "assets"
    os.makedirs(download_dir, exist_ok=True)

    if not filename:
        filename = url.split("/")[-1] 
        filename = urllib.parse.unquote(filename) #making it human readable
    filepath = os.path.join(download_dir, filename)

    try:
        response = requests.get(url, 
                                    stream=True, 
                                    headers=demo_headers, #to mimic the req as chrome@mac
                                    allow_redirects=True
                                    )

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        print(f"File {filename} downloaded successfully!")
        return filepath

    except Exception as e:
        print(f"Error while downloading: {e}")
        return False



if __name__ == "__main__" :
    url = "https://dam.assets.ohio.gov/raw/upload/ohiodnr.gov/documents/oil-gas/production/20210309_2020_1%20-%204.xls"
    download_file(url)
