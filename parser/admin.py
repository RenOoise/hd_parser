from django.contrib import admin

from .models import TaskExecutor, Task


@admin.register(TaskExecutor)
class TaskExecutorAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'fullname'
                    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'external_id',
                    'task_name',
                    'task_creator_name',
                    'task_executor',
                    'task_changed'
                    )
