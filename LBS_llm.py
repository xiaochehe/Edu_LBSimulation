import os
import pandas as pd
from openai import OpenAI
import re
import os
import json
from tqdm import tqdm

def remove_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>\s*Reflections:\s*", "", text, flags=re.DOTALL)

def extract_final_prediction(text: str):
    match = re.search(r"Final_Prediction:\s*([1-7])", text)
    if match:
        return int(match.group(1))
    return None

# 定义映射关系 
mapping = {
    '教育心理学': 'edu_psy',
    '学习科学': 'lea_sci',
    '教育技术': 'edu_tech',
    '社会文化': 'soc_edu',
    '测评': 'ass_mea'
}

# 定义测试题目
sacle_items = [
    "In a class like this, I prefer course material that really challenges me so I can learn new things.",
    "If I study in appropriate ways, then I will be able to learn the material in this course.",
    "When I take a test I think about how poorly I am doing compared with other students.",
    "I think I will be able to use what I learn in this course in other courses.",
    "I believe I will receive an excellent grade in this class.",
    "I'm certain I can understand the most difficult material presented in the readings for this course.",
    "Getting a good grade in this class is the most satisfying thing for me right now.",
    "When I take a test I think about items on other parts of the test I can't answer.",
    "It is my own fault if I don't learn the material in this course.",
    "It is important for me to learn the course material in this class.",
    "The most important thing for me right now is improving my overall grade point average, so my main concern in this class is getting a good grade.",
    "I'm confident I can learn the basic concepts taught in this course.",
    "If I can, I want to get better grades in this class than most of the other students.",
    "When I take tests I think of the consequences of failing.",
    "I'm confident I can understand the most complex material presented by the instructor in this course.",
    "In a class like this, I prefer course material that arouses my curiosity, even if it is difficult to learn.",
    "I am very interested in the content area of this course.",
    "If I try hard enough, then I will understand the course material.",
    "I have an uneasy, upset feeling when I take an exam.",
    "I'm confident I can do an excellent job on the assignments and tests in this course.",
    "I expect to do well in this class.",
    "The most satisfying thing for me in this course is trying to understand the content as thoroughly as possible.",
    "I think the course material in this class is useful for me to learn.",
    "When I have the opportunity in this class, I choose course assignments that I can learn from even if they don't guarantee a good grade.",
    "If I don't understand the course material, it is because I didn't try hard enough.",
    "I like the subject matter of this course.",
    "Understanding the subject matter of this course is very important to me.",
    "I feel my heart beating fast when I take an exam.",
    "I'm certain I can master the skills being taught in this class.",
    "I want to do well in this class because it is important to show my ability to my family, friends, employer, or others.",
    "Considering the difficulty of this course, the teacher, and my skills, I think I will do well in this class.",
    "When I study the readings for this course, I outline the material to help me organize my thoughts.",
    "During class time I often miss important points because I'm thinking of other things.",
    "When studying for this course, I often try to explain the material to a classmate or friend.",
    "I usually study in a place where I can concentrate on my course work.",
    "When reading for this course, I make up questions to help focus my reading.",
    "I often feel so lazy or bored when I study for this class that I quit before I finish what I planned to do.",
    "I often find myself questioning things I hear or read in this course to decide if I find them convincing.",
    "When I study for this class, I practice saying the material to myself over and over.",
    "Even if I have trouble learning the material in this class, I try to do the work on my own, without help from anyone.",
    "When I become confused about something I'm reading for this class, I go back and try to figure it out.",
    "When I study for this course, I go through the readings and my class notes and try to find the most important ideas.",
    "I make good use of my study time for this course.",
    "If course readings are difficult to understand, I change the way I read the material.",
    "I try to work with other students from this class to complete the course assignments.",
    "When studying for this course, I read my class notes and the course readings over and over again.",
    "When a theory, interpretation, or conclusion is presented in class or in the readings, I try to decide if there is good supporting evidence.",
    "I work hard to do well in this class even if I don't like what we are doing.",
    "I make simple charts, diagrams, or tables to help me organize course material.",
    "When studying for this course, I often set aside time to discuss course material with a group of students from the class.",
    "I treat the course material as a starting point and try to develop my own ideas about it.",
    "I find it hard to stick to a study schedule.",
    "When I study for this class, I pull together information from different sources, such as lectures, readings, and discussions.",
    "Before I study new course material thoroughly, I often skim it to see how it is organized.",
    "I ask myself questions to make sure I understand the material I have been studying in this class.",
    "I try to change the way I study in order to fit the course requirements and the instructor's teaching style.",
    "I often find that I have been reading for this class but don't know what it was all about.",
    "I ask the instructor to clarify concepts I don't understand well.",
    "I memorize key words to remind me of important concepts in this class.",
    "When course work is difficult, I either give up or only study the easy parts.",
    "I try to think through a topic and decide what I am supposed to learn from it rather than just reading it over when studying for this course.",
    "I try to relate ideas in this subject to those in other courses whenever possible.",
    "When I study for this course, I go over my class notes and make an outline of important concepts.",
    "When reading for this class, I try to relate the material to what I already know.",
    "I have a regular place set aside for studying.",
    "I try to play around with ideas of my own related to what I am learning in this course.",
    "When I study for this course, I write brief summaries of the main ideas from the readings and my class notes.",
    "When I can't understand the material in this course, I ask another student in this class for help.",
    "I try to understand the material in this class by making connections between the readings and the concepts from the lectures.",
    "I make sure that I keep up with the weekly readings and assignments for this course.",
    "Whenever I read or hear an assertion or conclusion in this class, I think about possible alternatives.",
    "I make lists of important items for this course and memorize the lists.",
    "I attend this class regularly.",
    "Even when course materials are dull and uninteresting, I manage to keep working until I finish.",
    "I try to identify students in this class whom I can ask for help if necessary.",
    "When studying for this course I try to determine which concepts I don't understand well.",
    "I often find that I don't spend very much time on this course because of other activities.",
    "When I study for this class, I set goals for myself in order to direct my activities in each study period.",
    "If I get confused taking notes in class, I make sure I sort it out afterwards.",
    "I rarely find time to review my notes or readings before an exam.",
    "I try to apply ideas from course readings in other class activities such as lecture and discussion."
]

ori_prompt = '''Task: What you see above is an interview transcript and relevant expert reflections. Based on these content, I want you to predict the student's survey responses. The survey uses a seven-point Likert scale, ranging from “not at all true of me” to “very true of me.”The  question is single choice, and your task is to infer the student’s most probable selection. As you answer, I want you to take the following steps: Step 1) Describe in a few sentences the kind of person that would choose each end of the range; Step 2) Write a few sentences reasoning on which option best predicts the student's response; Step 3) Predict how the student will actually respond among the options 1 to 7.Predict based on the interview and your thoughts. \n Here is the question:'''

trailer = 'Output format: Final_Prediction: a number between 1 and 7'


# 文件路径
csv1_path = "1.csv"
csv2_path = "2.csv"
dialog_folder_base = "4"  # 假设所有对话文件夹在这个路径下
base_folder = 'expert'

client = OpenAI(
    base_url="http://222.195.133.39:8000/v1",
    api_key="token-abc123",
)

# 读取 CSV
df1 = pd.read_csv(csv1_path)  # 对话专家排序信息
df2 = pd.read_csv(csv2_path)  # 预测题目信息

# 假设 df1 包含列：dialog_id, expert_name, rank
# 假设 df2 包含列：Item, top1_dialog, top2_dialog
# 你可以根据实际列名修改

for person in os.listdir(base_folder):
    dialog_folder_base = os.path.join(base_folder, person)
    def get_expert_analysis(dialog_id, top_n=2):
        """获取指定对话的前 top_n 位专家分析文本"""
        # 获取对话对应的前 N 位专家
        experts = df1[df1['Item'] == dialog_id]['Expert'].values[0]
        print(dialog_id,experts)
        experts = [s.strip() for s in experts.split(">")]
        experts = [mapping.get(item, item) for item in experts][:top_n]
        
        analyses = []
        for expert in experts:
            file_path = os.path.join(dialog_folder_base, f"{dialog_id}", f"{expert}.txt")
            if os.path.exists(file_path):
                # 尝试多种编码格式
                encodings = ['utf-8', 'gbk', 'gb18030', 'latin-1']

                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            # print(file_path)
                            analyses.append(f.read())
                        break  # 如果成功读取，跳出循环
                    except UnicodeDecodeError:
                        continue  # 如果当前编码失败，尝试下一个
                else:
                    # 如果所有编码都失败，使用忽略错误的方式
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        print(file_path)
                        analyses.append(f.read())

                # with open(file_path, 'r', encoding='utf-8') as f:
                #     print(file_path)
                #     analyses.append(f.read())
            else:
                print(f"Warning: 文件不存在 {file_path}")
        return analyses

    # 遍历每个预测题目
    prediction_results = {}
    prediction_results_json = dialog_folder_base + '.json'

    for idx, row in tqdm(df2.iterrows()):
        item = row['Item']
        top1_dialog = row['Top1'] + 8
        top2_dialog = row['Top2'] + 8

        scale_item = sacle_items[item-1]
        
        # 获取两个对话的专家分析
        analyses_top1 = get_expert_analysis(top1_dialog, top_n=2)
        analyses_top2 = get_expert_analysis(top2_dialog, top_n=2)
        
        # 合并所有参考分析
        combined_analyses = analyses_top1 + analyses_top2
        combined_analyses = '\n'.join(combined_analyses)
        print(combined_analyses)
        prompt = combined_analyses + '\n' + ori_prompt + scale_item + '\n' + trailer

        # print(prompt)

        completion = client.chat.completions.create(
                model="Qwen/Qwen3-8B",
                messages=[
                    {"role": "user", "content": prompt}
                ]
                )
        return_content = completion.choices[0].message.content
        return_content = remove_think_tags(return_content)
        return_content = extract_final_prediction(return_content)
        print(return_content)
        prediction_results[str(item)] = return_content
    with open(prediction_results_json, 'w') as f:
        json.dump(prediction_results, f)
