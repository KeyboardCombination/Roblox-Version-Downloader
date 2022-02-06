#Lannuked
import requests
import os
import json
import re
import time
from pprint import pformat

headersIn = {'User-Agent': 'Roblox/WinINet'}
assetUrl = "https://assetdelivery.roblox.com/v1/"
TimeInMil = int(round(time.time() * 1000))

badChars = ['"', ":"]
goodChars = ["'", "-"]

def createFold(FolderName):
    if not os.path.exists(FolderName):
        os.makedirs(FolderName)
    return FolderName

def logIt(toLog): 
    open(f"{createFold('logs')}/log Archive-{TimeInMil}.txt", "a").write(f'{str(toLog)}\n')

def yesOrNo(inputStr):
    boolAsk = input(inputStr)[0:1]
    if re.findall("[yY]", boolAsk):
        return True
    elif re.findall("[nN]", boolAsk):
        return False
    else:
        print("Invalid response, try one of the Y (Yes) or N (No) keys")
        return yesOrNo(inputStr)

def fixBadStr(inputStr):
    outputString = re.sub("[*/\\\\<>?|]", '', inputStr)
    for i in range(len(badChars)):
        outputString = outputString.replace(badChars[i], goodChars[i])
    return outputString

def Get(getFrom, getWhat):
    return getFrom.get(getWhat, '')

def addToName(ifVar, equalsThisVal):
    if ifVar: return equalsThisVal;
    else: return "";

downloaderVer = "v3.02a"

print(f"\nNukley's Asset Downloader ({downloaderVer})")
while True:
    try:
        assetIDStart = int(input("Enter an Asset ID: "))
        assetIDEnd = int(input("Enter an ending ID: "))
    except ValueError:
        print("\nInvalid Value(s), try again.\n")
        continue
    break

downloadAll = yesOrNo("Download all versions (Y/N): ")
versionCount = int(downloadAll)
firstOrLast = None

if downloadAll == False:
    firstOrLast = yesOrNo("Download first (Y) or last (N) version: ")

idInName = yesOrNo("Put ID's in filename? (Y/N): ")
timeInName = yesOrNo("Put Dates in filename? (Y/N): ")
userDir = yesOrNo("Put assets in a folder with the creators name? (Y/N): ")
assetDir = yesOrNo("Put assets in a folder with the assets name and ID? (Y/N): ")
getJson = yesOrNo("Put asset details in file directory? (Y/N): ")

#BEGIN-AssetTypeIDs
idk = "Unknown"
#assetTypeId = place in table
assetTypeList = ["Image", "TShirt", "Audio", "Mesh", "Lua", "HTML", "Text",
"Hat", "Place", "Model", "Shirt", "Pants", "Decal", idk, idk, idk, "Avatar","Head", "Face", "Gear",
idk, idk, "Badge", "GroupEmblem", idk, "Animation", "Arms", "Legs", "Torso", "RightArm", "LeftArm",
"LeftLeg", "RightLeg", "Package", "YouTubeVideo", "GamePass", "App", idk, "Code", "Plugin",
"SolidModel", "MeshPart", "HairAccessory", "NeckAccessory", "ShoulderAccessory", "FrontAccessory",
"BackAccessory", "WaistAccessory", "ClimbAnimation", "DeathAnimation", "FallAnimation",
"IdleAnimation", "JumpAnimation", "RunAnimation", "SwimAnimation", "WalkAnimation", "PoseAnimation",
"EarAccessory", "EyeAccessory", "LocalizationTableManifest", "LocalizationTableTranslation",
"EmoteAnimation", "Video", "TexturePack", "TShirtAccessory", "ShirtAccessory", "PantsAccessory",
"JacketAccessory", "SweaterAccessory", "ShortsAccessory", "LeftShoeAccessory", "RightShoeAccessory",
"DressSkirtAccessory"]

def assetExt():
    if assetTypeId == 1: fileExt = ".png"
    elif assetTypeId == 3: fileExt = ".mp3"
    elif assetTypeId == 4: fileExt = ".mesh"
    elif assetTypeId == 5: fileExt = ".lua"
    elif assetTypeId == 9: fileExt = ".rbxl"
    else: fileExt = ".rbxm"
    return fileExt
#END---AssetTypeIDs

for inc in range(assetIDStart, assetIDEnd + 1):
    maxVerId = requests.get(f'{assetUrl}assetid/{inc}', headers = headersIn)
    versionNumber = Get(maxVerId.headers, "roblox-assetversionnumber")
    if versionNumber == '' and versionCount == 1:
        print(f"Asset {inc} is copylocked or invalid!")
        continue
    else:
        print(f"Asset {inc} has {versionNumber} version(s)!")

        if firstOrLast: versionCount = versionNumber = 1
        elif firstOrLast == False: versionCount = int(versionNumber)

    try:
        getAssetJson = requests.get(f'http://api.roblox.com/Marketplace/ProductInfo?assetId={inc}')

        assetInfo = getAssetJson.json()
        assetName = Get(assetInfo, "Name")
        assetTypeId = Get(assetInfo, "AssetTypeId")
        creatorName = Get(Get(assetInfo, "Creator"), "Name")
        AssetTypeName = assetTypeList[assetTypeId - 1]
    except TimeoutError:
        print("Connection Failed, Retrying")
        time.sleep(10)
        continue
    except Exception as TheError:
        print("Error logged!")
        logIt(TheError)

    for Counter in range(versionCount, int(versionNumber) + 1):
        try:
            dlAsset = requests.get(f'{assetUrl}asset/?id={inc}&version={Counter}', headers = headersIn)
            assetDate = addToName(timeInName, f" ({fixBadStr(Get(dlAsset.headers, 'Last-Modified')[5:-4])})")
            status = dlAsset.status_code

            versionInName = f" (v{Counter})"
            creatorInName = addToName(userDir, f"({creatorName})")
            putIdInName = addToName(idInName, f"({inc}) ")
            nameAndId = f"{putIdInName}[{fixBadStr(assetName)}]"
            nameIdInName = addToName(assetDir, nameAndId)
            idNameVer = (f"{nameAndId}{versionInName}")

            if (status != 200):
                print(f"v{Counter} {status}'d! Skipping...")
                continue

            print(f'Saving {AssetTypeName}: {inc} "{assetName}"{versionInName}')
            createDir = createFold((f'Archive-{TimeInMil}/{creatorInName}/{AssetTypeName}/{nameIdInName}'))
            open(f"{createDir}/{idNameVer}{assetDate}{assetExt()}", "wb").write(dlAsset.content)

            if getJson:
                open(f"{createDir}/{nameAndId}.json", "w", encoding = "utf-8").write(str(pformat(assetInfo)))

            if (downloadAll == False):
                break
        except TimeoutError:
            print("Connection Failed, Retrying")
            time.sleep(10)
            continue
        except Exception as TheError:
            print("Error logged!")
            logIt(TheError)

print('Done Downloading!')