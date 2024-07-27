from requests import get
from lxml import etree
from datetime import datetime
from re import search

query = str(input('조회할 법령의 이름을 입력하세요: '))

def xmlDict(element):
    if len(element) == 0:
        return element.text
    result = {}
    for child in element:
        child_dict = xmlDict(child)
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_dict)
        else:
            result[child.tag] = child_dict
    result.update(element.attrib)
    return result

def removeSpace(Text: str):
    return Text.replace("\n","").replace("\t","").lstrip().rstrip()

try:
    Datas = get(
        'http://apis.data.go.kr/1170000/law/lawSearchList.do',
        params = {
            'serviceKey' : '',
            'target' : 'law',
            'query' : query,
            'numOfRows' : '1',
            'pageNo' : '1',
        }
    )
    Data = xmlDict(etree.fromstring(Datas.content))['law']
    print("{} {}".format(Data['법령명한글'], f"( 약칭: {Data['법령약칭명']} )" if len(Data['법령약칭명']) else ""))
    print("[시행 {}] [법률 제{}호, {}, {}]".format(datetime.strptime(Data['시행일자'], '%Y%m%d').strftime('%Y. %m. %d.'), Data['공포번호'], datetime.strptime(Data['공포일자'], '%Y%m%d').strftime('%Y. %m. %d.'), Data['제개정구분명']))
    print("- {}".format(str(Data['소관부처명']).replace(",", "\n- ") if Data['소관부처명'] else '정보없음'))
    print("\n전문보기 → https://law.go.kr{}".format(Data['법령상세링크']))
    JO = input("\n조항 번호 입력(n조의n인 경우 공백으로 구분): ").split()
    subDatas = get(
        'https://www.law.go.kr/DRF/lawService.do',
        params = {
            'OC': search(r'OC=([^&]+)', Data['법령상세링크']).group(1),
            'target': 'lawjosub',
            'type': 'XML',
            'ID': Data['법령ID'],
            'JO': JO[0].zfill(4)+(JO[1].zfill(2) if len(JO) > 1 else '00'),
        }
    )
    subData = xmlDict(etree.fromstring(subDatas.content))
    try:
        subTemp = []
        if type(subData['조문']['조문단위']) == list:
            subTemp = subData['조문']['조문단위']
        else:
            subTemp.append(subData['조문']['조문단위'])
        try:
            for subData0 in subTemp:
                try:
                    print(removeSpace(subData0['조문내용']))
                    for subData1 in subData0['항']:
                        try:
                            print(f"  {removeSpace(subData1['항내용'])}")
                            for subData2 in subData1['호']:
                                try:
                                    print(f"    {removeSpace(subData1['호내용'])}")
                                    for subData3 in subData2['목']:
                                        try:
                                            print(f"      {removeSpace(subData1['목내용'])}")
                                        except:
                                            continue
                                except:
                                    continue
                        except:
                            continue
                except:
                    continue
        except:
            pass
    except:
        pass
except:
    print("조회 결과가 없습니다.")
