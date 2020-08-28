from common.fetchMpl import *

def main():

    start, end,read_time = timeRange()

    mplLink = ".hana.ondemand.com/api/v1/MessageProcessingLogs/?$inlinecount=allpages&$filter=(Status eq 'FAILED' or Status eq 'ESCALATED')\
     and LogEnd gt datetime'" + str(start) + "' and LogEnd lt datetime'" + str(end) + "'"

    logData,errorCount=startFetch(Tenants,mplLink)
    checkError(Tenants,errorCount)

    #provide Client,CheckGroup,CheckID,SystemRole Values:

    # DEV Data,URL
    extendData=["v0120","IBSO_DNT","00006","FSN"]
    url = "https://api-smartops-dev.cfapps.sap.hana.ondemand.com/ibso/cpi"

    # PROD Data
    #extendData=["","IBSO_EXT","00002","FSN"]
    #url = "https://api-smartops.cfapps.us10.hana.ondemand.com/ibso/cpi"

    pushErrorData=format_data(logData,url,extendData)
    pushErrorCheck(pushErrorData)
    updateTime(read_time)

main()


