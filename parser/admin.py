from django.contrib import admin

from .models import TaskExecutor, Task, ExecutorsAndTasksId


@admin.register(TaskExecutor)
class TaskExecutorAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'fullname',
                    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'external_id',
                    'task_name',
                    'task_creator_name',
                    'task_changed',
                    )


@admin.register(ExecutorsAndTasksId)
class ExecutorsAndTasksIdAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'task_id',
                    'executor_id',
                    )
