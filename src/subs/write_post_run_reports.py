import collections
import statistics
import time
import os
from os.path import join
from pathlib import Path
from pprint import pprint


if __name__ == "__main__":
    import sys, pathlib
    sys.path.append(str(pathlib.Path(__file__).parent.parent))

from YT_PL_DL_Data import YT_PL_DL_Data
from get_real_episode_sub_data_from_auto_sub import get_real_episode_sub_data_from_auto_sub
from trim_and_re_time_real_sub_file_from_auto_subs import trim_and_re_time_real_sub_file_from_auto_subs
from Series_Sub_Map import Series_Sub_map

from sms.file_system_utils import file_system_utils as fsu
from sms.logger import json_logger
import vid_edit_utils as veu
import subtitle_utils
import cfg
import sub_diff_ratio_tools

# SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__))
POST_RUN_REPORTS_DIR_PATH = join(cfg.INIT_MKVS_WORKING_DIR_PATH, "post_run_reports")
POST_RUN_REPORT_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "post_run_report.json")
WRONG_ANSWERS_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "wrong_answers.json")
CLIP_NAME_CHOSEN_SUB_PATH_OD__LAST_RUN__JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "clip_name_chosen_sub_path_od__last_run.json")
CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__JSON_PATH             = join(POST_RUN_REPORTS_DIR_PATH, "clip_name_chosen_sub_path_l_od__correct_answers.json")
CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__SORTED_ABC__JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "clip_name_chosen_sub_path_l_od__correct_answers__sorted_abc.json")
RUN_LOG_L__SORTED_BY__BEST_AVG_LINE_DIALOG_FUZZ_RATIO_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "run_log_l__sorted_by__best_avg_line_dialog_fuzz_ratio.json")
RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "run_log_l__sorted_by__best_sub_diff_ratio.json")
RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH = join(POST_RUN_REPORTS_DIR_PATH, "run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d.json")



def write_run_log_l__sorted_by__best_avg_line_dialog_fuzz_ratio():
    def _get_best_sub_dir_ratio(clip_data_d):
        best_avg_line_dialog_fuzz_ratio = 0

        if "avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d" in clip_data_d.keys():
            avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d = clip_data_d["avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d"]
            best_avg_line_dialog_fuzz_ratio = 1
            
            if len(avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d) != 0:
                best_avg_line_dialog_fuzz_ratio_str = max(avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d.keys())
                # best_sub_path_l = sub_diff_ratio_sub_path_l_d[best_avg_line_dialog_fuzz_ratio]
                best_avg_line_dialog_fuzz_ratio = float(best_avg_line_dialog_fuzz_ratio_str)
        return best_avg_line_dialog_fuzz_ratio

    run_log_l = json_logger.read(cfg.RUN_LOG_JSON_PATH)

    sorted_run_log_l = sorted(run_log_l, key=lambda clip_data_d: _get_best_sub_dir_ratio(clip_data_d), reverse = True)

    # put keys in order
    new_log_l = []
    for clip_data_d in sorted_run_log_l:
        if "sub_diff_ratio_sub_path_l_d" in clip_data_d.keys():
            clip_data_d["sub_diff_ratio_sub_path_l_d"] = collections.OrderedDict(sorted(clip_data_d["sub_diff_ratio_sub_path_l_d"].items()))
        if "avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d" in clip_data_d.keys():
            clip_data_d["avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d"] = collections.OrderedDict(sorted(clip_data_d["avg_most_confident_line_dialog_fuzz_ratio_sub_path_l_d"].items(), reverse=True))
        new_log_l.append(clip_data_d)

    print(f"Writing {RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH}...")
    json_logger.write(sorted_run_log_l, RUN_LOG_L__SORTED_BY__BEST_AVG_LINE_DIALOG_FUZZ_RATIO_JSON_PATH)

def write_run_log_l__sorted_by__best_sub_diff_ratio():
    def _get_best_sub_dir_ratio(clip_data_d):
        best_sub_diff_ratio = 9999

        if "sub_diff_ratio_sub_path_l_d" in clip_data_d.keys():
            sub_diff_ratio_sub_path_l_d = clip_data_d["sub_diff_ratio_sub_path_l_d"]
            best_sub_diff_ratio = 999
            
            if len(sub_diff_ratio_sub_path_l_d) != 0:
                best_sub_diff_ratio_str = min(sub_diff_ratio_sub_path_l_d.keys())
                best_sub_path_l = sub_diff_ratio_sub_path_l_d[best_sub_diff_ratio_str]
                best_sub_diff_ratio = float(best_sub_diff_ratio_str)
        return best_sub_diff_ratio

    run_log_l = json_logger.read(cfg.RUN_LOG_JSON_PATH)

    sorted_run_log_l = sorted(run_log_l, key=lambda clip_data_d: _get_best_sub_dir_ratio(clip_data_d))
    print(f"Writing {RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH}...")
    json_logger.write(sorted_run_log_l, RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH)


def write_run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d():
    sorted_run_log_l = json_logger.read(RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS_JSON_PATH)
    new_log_l = []

    for clip_data_d in sorted_run_log_l:
        if "sub_diff_ratio_sub_path_l_d" in clip_data_d.keys():
            clip_data_d["sub_diff_ratio_sub_path_l_d"] = collections.OrderedDict(sorted(clip_data_d["sub_diff_ratio_sub_path_l_d"].items()))
        new_log_l.append(clip_data_d)

    print(f"Writing {RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH}...")
    json_logger.write(sorted_run_log_l, RUN_LOG_L__SORTED_BY__BEST_SUB_DIFF_RATIOS__W_SORTED__SUB_DIFF_RATIO_SUB_PATH_L_D_JSON_PATH)


# def write_clip_name_chosen_sub_path_od__from__run_log_l_json(run_log_l_json_path, out_json_path):
def _get_clip_name_chosen_sub_path_od__from__run_log_l_json(run_log_l_json_path):
    sorted_run_log_l = json_logger.read(run_log_l_json_path)
    clip_name_chosen_sub_path_od = collections.OrderedDict()

    for clip_data_d in sorted_run_log_l:
        chosen_sub_path = None
        if "chosen_sub_path" in clip_data_d.keys():
            chosen_sub_path = clip_data_d["chosen_sub_path"]
       
        clip_name = clip_data_d["clip_name"]
        clip_name_chosen_sub_path_od[clip_name] = chosen_sub_path
    return clip_name_chosen_sub_path_od

    # json_logger.write(clip_name_chosen_sub_path_od, out_json_path)

def write_clip_name_chosen_sub_path_od__last_run__from__run_log_l_json(run_log_l_json_path, out_json_path):
    clip_name_chosen_sub_path_od = clip_name_chosen_sub_path_od(run_log_l_json_path)
    json_logger.write(clip_name_chosen_sub_path_od, out_json_path)

def write_clip_name_chosen_sub_path_l_od__correct_answers__from__run_log_l_json(run_log_l_json_path, prev_correct_answers_json_path = None, out_json_path = None):
    if prev_correct_answers_json_path == None and out_json_path == None:
        raise ValueError("Error: invalid params")
    
    if out_json_path == None:
        out_json_path == prev_correct_answers_json_path

    run_log__clip_name_chosen_sub_path_od = _get_clip_name_chosen_sub_path_od__from__run_log_l_json(run_log_l_json_path)

    # Build new_correct_answers__clip_name_chosen_sub_path_l_od
    new_correct_answers__clip_name_chosen_sub_path_l_od = collections.OrderedDict()
    # No prev correct answers json given
    if prev_correct_answers_json_path == None:
        for clip_name, chosen_sub_path in run_log__clip_name_chosen_sub_path_od.items():
            new_correct_answers__clip_name_chosen_sub_path_l_od[clip_name] = [chosen_sub_path]
    # Prev correct answers json given
    else:
        prev_correct_answers__clip_name_chosen_sub_path_l_od = json_logger.read(prev_correct_answers_json_path)
        for clip_name, chosen_sub_path in run_log__clip_name_chosen_sub_path_od:

            if clip_name not in prev_correct_answers__clip_name_chosen_sub_path_l_od.keys():
                raise ValueError(f"{run_log_l_json_path=} contains {clip_name=} which does not exist in in {prev_correct_answers_json_path=}, meaning that comparison is not valid.")

            prev_correct_answers_chosen_sub_path_l = prev_correct_answers__clip_name_chosen_sub_path_l_od[clip_name]

            if chosen_sub_path not in prev_correct_answers_chosen_sub_path_l:
                prev_correct_answers_chosen_sub_path_l.append(chosen_sub_path)

            new_correct_answers__clip_name_chosen_sub_path_l_od[clip_name] = prev_correct_answers_chosen_sub_path_l

    json_logger.write(new_correct_answers__clip_name_chosen_sub_path_l_od, out_json_path)


def write_clip_name_chosen_sub_path_l_od__correct_answers__sorted_abc(og_correct_answers__clip_name_chosen_sub_path_l_od__json_path, out_json_path):
    og_correct_answers__clip_name_chosen_sub_path_l_od = json_logger.read(og_correct_answers__clip_name_chosen_sub_path_l_od__json_path)
    sorted_abc__correct_answers__clip_name_chosen_sub_path_l_od = dict(sorted(og_correct_answers__clip_name_chosen_sub_path_l_od.items()))
    print("Writing sorted_abc__correct_answers__clip_name_chosen_sub_path_l_od to {out_json_path}...")
    json_logger.write(sorted_abc__correct_answers__clip_name_chosen_sub_path_l_od, out_json_path)


def write_wrong_answers_d_json(clip_name_chosen_sub_path_od__last_run__json_path, clip_name_chosen_sub_path_l_od__correct_answers__json_path):
    clip_name_chosen_sub_path_od__last_run = json_logger.read(clip_name_chosen_sub_path_od__last_run__json_path)
    clip_name_chosen_sub_path_l_od__correct_answers = json_logger.read(clip_name_chosen_sub_path_l_od__correct_answers__json_path)

    if len(clip_name_chosen_sub_path_od__last_run) != len(clip_name_chosen_sub_path_l_od__correct_answers):
        raise Exception(f"ERROR: {len(clip_name_chosen_sub_path_od__last_run)=} != {len(clip_name_chosen_sub_path_l_od__correct_answers)}, so the comparison will not be valid")

    wrong_answers_d = collections.OrderedDict()
    wrong_answers_d["num_correct"] = 0
    wrong_answers_d["num_wrong"] = 0
    wrong_answers_d["wrong"] = []

    for clip_name, chosen_sub_path in clip_name_chosen_sub_path_od__last_run.items():
        if clip_name not in clip_name_chosen_sub_path_l_od__correct_answers.keys():
            raise Exception("ERROR: last run contains a clip name not found in correct answers: ", clip_name)
        
        correct_chosen_sub_path_l = clip_name_chosen_sub_path_l_od__correct_answers[clip_name]

        if chosen_sub_path not in correct_chosen_sub_path_l:
            wrong_answers_d["wrong"].append({
                "clip_name": clip_name,
                "wrong_chosen_sub_path": chosen_sub_path,
                "correct_chosen_sub_path_l": correct_chosen_sub_path_l
            })

    num_wrong = len(wrong_answers_d["wrong"])
    wrong_answers_d["num_wrong"] = num_wrong
    wrong_answers_d["num_correct"] = len(clip_name_chosen_sub_path_od__last_run) - num_wrong

    json_logger.write(wrong_answers_d, WRONG_ANSWERS_JSON_PATH)

if __name__ == "__main__":
    import os.path as path
    print("Running " , path.abspath(__file__) , '...')
    # write_run_log_l__sorted_by__best_sub_diff_ratio()
    # write_run_log_l__sorted_by__best_sub_diff_ratio__w_sorted__sub_diff_ratio_sub_path_l_d()
    # write_run_log_l__sorted_by__best_avg_line_dialog_fuzz_ratio()
    # write_clip_name_chosen_sub_path_od__last_run__from__run_log_l_json(RUN_LOG_L__SORTED_BY__BEST_AVG_LINE_DIALOG_FUZZ_RATIO_JSON_PATH, CLIP_NAME_CHOSEN_SUB_PATH_OD__LAST_RUN__JSON_PATH)

    # # write_clip_name_chosen_sub_path_l_od__correct_answers__from__run_log_l_json(run_log_l_json_path = RUN_LOG_L__SORTED_BY__BEST_AVG_LINE_DIALOG_FUZZ_RATIO_JSON_PATH,
    # #                                                                             prev_correct_answers_json_path = CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__JSON_PATH,
    # #                                                                             out_json_path = CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__JSON_PATH)
    
    write_clip_name_chosen_sub_path_l_od__correct_answers__sorted_abc(CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__JSON_PATH, CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__SORTED_ABC__JSON_PATH)

    # write_wrong_answers_d_json(CLIP_NAME_CHOSEN_SUB_PATH_OD__LAST_RUN__JSON_PATH, CLIP_NAME_CHOSEN_SUB_PATH_l_OD__CORRECT_ANSWERS__JSON_PATH)
    print("End of Main") 
