from collections import defaultdict
from django.db.models import Sum, Count
import itertools
from operator import attrgetter
from quests.models import Category, QuestAnswer, Quest
from teams.models import Team
from datetime import datetime

__author__ = 'Last G'

board_sql = """

select quest.*, category.name as category_name , sum(opens.id) as is_open ,sum(answer.id) as is_solved
from quests_quest quest
 join quests_category category on quest.category_id = category.id
 left join quests_quest_open_for opens on opens.quest_id = quest.id
 left join quests_questvariant variant   on variant.quest_id = quest.id
 left join quests_questanswer  answer    on answer.quest_variant_id = variant.id and answer.is_checked and answer.is_success
where
  opens.team_id = %s
group by quest.id
order by category.name, quest.score
"""

def groupby(collection, key):
    current = prev = object()
    res = []
    subres = []
    it = iter(collection)
    first = next(it)
    prev = getattr(first, key)
    subres.append(prev)
    for el in it:
        current = getattr(el, key)
        if current == prev:
            subres.append(el)
        else:
            res.append((prev, subres))
            prev = current
            subres = [el]
    if subres:
        res.append((prev, subres))
    return res



def get_task_board(team):
    quests = list(Quest.objects.raw(board_sql, [team.id]))
    print(len(quests))
#    by_category = itertools.groupby(quests, attrgetter('category_name'))
#    by_category = defaultdict(list)
#    for q in quests:
#        by_category[q.category.name].append(q)
    by_category = groupby(quests, 'category_name')
    return by_category


scores_sql = """
select team.*, sum(answer.score) as score
 from teams_team team
 left join quests_questvariant variant   on variant.team_id = team.id
-- left join quests_quest        quest     on quest.id = variant.quest_id
 left join quests_questanswer  answer    on answer.quest_variant_id = variant.id
 where
  (team.is_active and not team.is_staff and not team.is_superuser)
  and
  (
   (answer.is_checked and answer.is_success)
   or
   ( answer.id is null and answer.score is null )
  )
group by team.id
 order by score desc, max(answer.created_at)
"""


def scoreboard_modified(request, *args, **kwargs):
    try:
        time = QuestAnswer.objects.filter(is_checked=True, is_success=True).latest('created_at').created_at
        if time:
            return time
    except QuestAnswer.DoesNotExist:
        pass

    return datetime.now()


def get_scoreboard():
    answered = Team.objects.raw(scores_sql)
    return answered