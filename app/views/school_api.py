import copy
import json
from datetime import date as dt_module
from typing import Optional

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request as req
from requests import request

from app.config.config import get_config

bp = Blueprint(
    name="school_api",
    import_name="school_api",
    url_prefix="/api"
)

allergy_lists = ["난류", "우유", "메밀", "땅콩", "대두", "밀", "고등어", "게", "새우", "돼지고기", "복숭아",
                 "토마토", "아황산염", "호두", "닭고기", "쇠고기", "오징어", "조개류(굴,전복,홍합 등)"]


class SchoolClient:
    def __init__(self, token: str):
        self.token = token
        self.BASE = "https://open.neis.go.kr"

    def request(self, method: str, path: str, **kwargs):
        params = {
            "KEY": self.token,
            "Type": "json"
        }
        url = "{0}{1}".format(self.BASE, path)

        if "params" not in kwargs:
            kwargs['params'] = params
        else:
            kwargs['params'].update(params)

        response = request(
            method, url, **kwargs
        )

        if response.headers.get("Content-Type").startswith("application/json;"):
            result = response.json()
        else:
            result = response.text
            result = json.loads(result)

        return result

    def get(self, path: str, **kwargs):
        return self.request(
            method="GET",
            path=path,
            **kwargs
        )


@bp.route("/school", methods=['GET'])
def school():
    parser = get_config()
    if not parser.has_option("token", "neis"):
        return make_response(
            jsonify({
                "CODE": 401,
                "MESSAGE": "neis OpenAPI token is missing."
            }),
            401
        )

    args = req.args
    if "name" not in args:
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Missing school name."
            }),
            400
        )

    name: str = args["name"]
    provincial: Optional[str] = args.get("provincial", default=None)
    sc_code: Optional[str] = args.get("code", default=None)
    sc_type: Optional[int] = args.get("type", default=None, type=int)
    page: Optional[int] = args.get("page", default=1, type=int)

    if sc_type is not None and not 0 <= sc_type < 4:
        # 0: 초등학교 / 1: 중학교 / 2: 고등학교 / 3: 특수학교
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Type index out of range. ( 0 <= {0} <= 3)".format(
                    sc_type
                )
            }),
            400
        )

    client = SchoolClient(
        token=parser.get('token', 'neis')
    )
    params = {
        "pSize": 1000,
        "SCHUL_NM": name
    }

    __sc_type = ["초등학교", "중학교", "고등학교", "특수학교"]
    if sc_type is not None:
        _sc_type = __sc_type[sc_type]
        params["SCHUL_KND_SC_NM"] = _sc_type
    if provincial is not None:
        params["ATPT_OFCDC_SC_CODE"] = provincial
    if sc_code is not None:
        params["SD_SCHUL_CODE"] = sc_code
    if sc_code is not None:
        params["SD_SCHUL_CODE"] = sc_code
    if page is not None:
        params["pIndex"] = page

    result = client.get(
        path="/hub/schoolInfo",
        params=params
    )

    if "RESULT" in result:
        return make_response(
            jsonify(result),
            400
        )
    elif "schoolInfo" in result:
        result = result.get("schoolInfo")

    # Based on https://open.neis.go.kr/
    head, row = result

    total = 0
    final_result = []
    for h in head['head']:
        if "list_total_count" not in h:
            continue
        total = h["list_total_count"]

    for _sc in row['row']:
        final_result.append({
            "provincial_code": _sc.get("ATPT_OFCDC_SC_CODE", ""),
            "provincial": _sc.get("ATPT_OFCDC_SC_NM", ""),
            "code": _sc.get("SD_SCHUL_CODE", ""),
            "name": _sc.get("SCHUL_NM", ""),
            "eng_name": _sc.get("ENG_SCHUL_NM", ""),
            "type": _sc.get("SCHUL_KND_SC_NM", ""),
            "address": _sc.get("ORG_RDNMA", ""),
            "telephone": _sc.get("ORG_TELNO", "")
        })

    return make_response(
        jsonify({
            "data": final_result,
            "total": total,
            "current": page
        }),
        200
    )


@bp.route("/meal", methods=['GET'])
def meal():
    parser = get_config()
    if not parser.has_option("token", "neis"):
        return make_response(
            jsonify({
                "CODE": 401,
                "MESSAGE": "neis OpenAPI token is missing."
            }),
            401
        )

    args = req.args
    if "provincial" not in args:
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Missing provincial."
            }),
            400
        )
    if "code" not in args:
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Missing school code."
            }),
            400
        )
    if "date" in args and ("start_date" not in args or "end_date" not in args):
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Don't put in start/end date and date at the same time."
            }),
            400
        )
    if "start_date" in args and "end_date" not in args:
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Missing end date."
            }),
            400
        )
    if "start_date" not in args and "end_date" in args:
        return make_response(
            jsonify({
                "CODE": 400,
                "MESSAGE": "Missing start date."
            }),
            400
        )

    provincial: str = args["provincial"]
    sc_code: str = args["code"]
    page: Optional[int] = args.get("page", default=1, type=int)

    date: Optional[str] = args.get(
        "date",
        default=dt_module.today().strftime("%Y%m%d")
    )
    start_date: Optional[str] = args.get("start_date", default=None)
    end_date: Optional[str] = args.get("end_date", default=None)

    client = SchoolClient(
        token=parser.get('token', 'neis')
    )

    params = {
        "pSize": 1000,
        "ATPT_OFCDC_SC_CODE": provincial,
        "SD_SCHUL_CODE": sc_code
    }

    if page is not None:
        params["pIndex"] = page
    if date is not None:
        params["MLSV_YMD"] = date
    if start_date is not None and end_date is not None:
        params["MLSV_FROM_YMD"] = start_date
        params["MLSV_TO_YMD"] = end_date

    result = client.get(
        path="/hub/mealServiceDietInfo",
        params=params
    )

    if "RESULT" in result:
        return make_response(
            jsonify(result),
            400
        )
    elif "mealServiceDietInfo" in result:
        result = result.get("mealServiceDietInfo")

    # Based on https://open.neis.go.kr/
    head, row = result

    final_result = []

    for _sc in row['row']:
        meal_data = _sc.get("DDISH_NM").split("<br/>")
        allergy = []
        for index, _ in enumerate(meal_data):
            allergy_cache = []
            for j in range(18, 0, -1):
                if "{}.".format(j) in meal_data[index]:
                    allergy_cache.append(allergy_lists[j-1])
                meal_data[index] = meal_data[index].replace("{}.".format(j), "")
            allergy_cache.reverse()
            allergy.append(allergy_cache)

        origin = dict()
        origin_data = _sc.get("ORPLC_INFO").split("<br/>")
        for i in origin_data:
            key = i.split(":")[0].strip()
            value = i.split(":")[1].strip()
            origin[key] = value

        nutrition = dict()
        nutrition_data = _sc.get("NTR_INFO").split("<br/>")
        for i in nutrition_data:
            key = i.split(":")[0].strip()
            value = i.split(":")[1].strip()
            nutrition[key] = value

        final_result.append({
            "provincial_code": _sc.get("ATPT_OFCDC_SC_CODE", ""),
            "provincial": _sc.get("ATPT_OFCDC_SC_NM", ""),
            "code": _sc.get("SD_SCHUL_CODE", ""),
            "name": _sc.get("SCHUL_NM", ""),
            "date": _sc.get("MLSV_YMD", ""),
            "calorie": _sc.get("CAL_INFO", ""),
            "type": _sc.get("MMEAL_SC_NM", ""),
            "meal": meal_data,
            "allergy": allergy,
            "origin": origin,
            "nutrition": nutrition
        })

    if start_date is None and end_date is None and 0 < len(final_result) < 4:
        tp = 1
        _mt_md = {
            "조식": None,
            "중식": None,
            "석식": None
        }
        for _meal in final_result:
            _mt_md[_meal["type"]] = {
                "meal": _meal["meal"],
                "allergy": _meal["allergy"],
                "origin": _meal["meal"],
                "nutrition": _meal["nutrition"]
            }
        _final_result = copy.copy(final_result[0])

        _final_result.pop("meal")
        _final_result.pop("allergy")
        _final_result.pop("origin")
        _final_result.pop("nutrition")

        _final_result["breakfast"] = _mt_md["조식"]
        _final_result["lunch"] = _mt_md["중식"]
        _final_result["dinner"] = _mt_md["석식"]
    else:
        tp = 0
        _final_result = final_result

    return make_response(
        jsonify({
            "type": tp,
            "data": _final_result,
            "current": page
        }),
        200
    )
