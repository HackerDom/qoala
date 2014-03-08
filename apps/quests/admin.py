from django.contrib import admin

from . import models
# Register your models here.

class QuestAdmin(admin.ModelAdmin):
    fields = (
        'shortname',
        ('category', 'score'),
        ('provider_type', 'provider_file'),
        ('is_simple', 'is_manual'),
        'open_for', 'provider_hash'
    )
    readonly_fields = ('provider_type', 'provider_hash', 'category', 'score')
    list_display = ('shortname', 'category', 'score')
    list_filter = ('category', 'score')
    list_select_related = ('category',)
    search_fields = ('shortname',)
    filter_horizontal = ('open_for',)


class QuestVariantAdmin(admin.ModelAdmin):
    fields = (('team', 'quest'),
              'timeout',
              ('is_valid', 'try_count'),
              'html'
    )
    readonly_fields = ('html',)
    list_display = ('team', 'quest')
    list_filter = ('team', 'quest')
    list_select_related = ('quest', 'teams')
    search_fields = ('quest__shortname', 'team__name')

class QuestAnswerAdmin(admin.ModelAdmin):
    fields = ('quest_variant', ('score', 'is_checked', 'is_success'), 'answer', 'result')
    list_display = ('quest_name', 'team', 'is_checked', 'is_success', 'answer')
    list_filter = ('quest_variant__quest', 'quest_variant__team', 'is_checked', 'is_success')
    list_editable = ('is_checked', 'is_success')
    list_select_related = ('quest_variant',)
    search_fields = ('answer', 'quest_variant__quest__shortname')
#    readonly_fields = ('quest_name', 'team')
    def quest_name(self, obj):
        return obj.quest_variant.quest
    quest_name.short_description = 'Quest'

    def team(self, obj):
        return obj.quest_variant.team
    team.short_description = 'Team'

admin.site.register(models.Quest, QuestAdmin)
admin.site.register(models.QuestVariant, QuestVariantAdmin)
admin.site.register(models.QuestAnswer, QuestAnswerAdmin)