#coding:u8
# coding:u8
import leancloud

ConfigProduction = {
    "LEANCLOUD_APP_KEY": "bp8ie0RFdBG9nHkGHpOknCMQ",
    "LEANCLOUD_MASTER_KEY": "TzWRk7mT57Y19vewLB0A5pWk",
    "LEANCLOUD_APP_ID": "l7Ffw76ym9wuEsz4mUEJNcbS-gzGzoHsz",
    "OSS_ACCESS_KEY_ID": "LTAIkUlui2x5znBd",
    "OSS_ACCESS_KEY_SECRET": "a6wkpzmMGdGaCNb37JcKsZAkYKtKVZ",
    "OSS_ENDPOINT_HOST": "oss-cn-shanghai.aliyuncs.com",
    "OSS_ENDPOINT_HEAD": "http://",
    "OSS_BUCKET_NAME": "ailingual-production",
    "BAIDU_API_KEY": "2Qy9ddXQG2zzph38fIbSnttM",
    "BAIDU_SECRET_KEY": "09c715169f839ca12db6d3c46b539fcb"
}
ConfigStaging = {
    "LEANCLOUD_APP_ID": "hwB46P8KvcGH258ka0JfnMww-gzGzoHsz",
    "LEANCLOUD_APP_KEY": "ywhqmYxpFKTyemJrFl8YYT2j",
    "LEANCLOUD_MASTER_KEY": "Sr5rLnoJuGvTVxR3VtKOTQbK",
    "OSS_ACCESS_KEY_ID": "ZblgTWN34znE5dOO",
    "OSS_ACCESS_KEY_SECRET": "S09puSorYwkbdyyAjWpqudXQ8mLvl9",
    "OSS_ENDPOINT_HOST": "oss-cn-hangzhou.aliyuncs.com",
    "OSS_ENDPOINT_HEAD": "http://",
    "OSS_BUCKET_NAME": "xiaobandeng-staging",
    "BAIDU_API_KEY": "2Qy9ddXQG2zzph38fIbSnttM",
    "BAIDU_SECRET_KEY": "09c715169f839ca12db6d3c46b539fcb",
    "BOSON_API_KEY": "usdBIUiK.8823.g1JAM3QCmFpH",
    "TUOFENG_API_KEY": "3pkCWGefZQfXqGnd"
}


app_id = ConfigStaging["LEANCLOUD_APP_ID"]
app_key = ConfigStaging["LEANCLOUD_APP_KEY"]
app_master_key = ConfigStaging["LEANCLOUD_MASTER_KEY"]

# app_id = ConfigProduction["LEANCLOUD_APP_ID"]
# app_key = ConfigProduction["LEANCLOUD_APP_KEY"]
# app_master_key = ConfigProduction["LEANCLOUD_MASTER_KEY"]

leancloud.init(app_id, app_key, app_master_key)

ZhihuTopic =leancloud.Object.extend("ZhihuTopic")

#
# UserTranscript = leancloud.Object.extend("UserTranscript")
# Article = leancloud.Object.extend("Article")
# ArticleClass = leancloud.Object.extend("ArticleClassNew")
