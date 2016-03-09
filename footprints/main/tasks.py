from celery import task


@task
def demo_task():
    print("this is a demo celery task")
