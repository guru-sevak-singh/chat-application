import threading
from message_queue.message_queue import message_queue
from database import SessionalMaker
from models import Users, Rooms, Messages



def process_manager():
    '''
    This is the worker, and it continuous waiting for the message inside the queue,
    and when any message occur in the queue, it will run the task as per our queue.
    '''
    while True:
        job = message_queue.get()
        # db = SessionalMaker()
        try:
            print(f"Saving message to DB: {job}")

        except Exception as e:
            print('Error in Worker --> ', e)

        finally:
            message_queue.task_done()
    
def start_worker():
    thread = threading.Thread(target=process_manager, daemon=True)
    thread.start()
    print('Worker Thread Started...')
