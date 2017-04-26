//gcc -g ring.c -o ring -lpthread

#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <string.h>

pthread_mutex_t mut;
double sum;
int thread_qty;
char message[200];
sem_t* semaf;

void* thread_mess(void* rank)
{
	long my_rank = (long) rank;
	long dest = (my_rank + 1) % thread_qty;
	int i = 0;
	char a;
	
	while(1)
	{
		//printf("%ld waiting\n", my_rank);
		sem_wait(&semaf[my_rank]);
		for(;i<strlen(message);i++)
		{
			if(message[i] >= 'a' && message[i] <= 'z')
			{
				a = message[i] - 'a' + 'A';
				printf("Thread %ld changed %c to %c\n",my_rank,message[i],a);
				message[i] = a;
				break;
			}
		}
		sleep(1);
		sem_post(&semaf[dest]);
		if(i == strlen(message))
			break;
	}
	
	return NULL;
}

void main(int argc, char* argv[])
{
	long i;
	pthread_t* tid;
	thread_qty = 30;
	int l;
	
	srand(time(NULL));
	l = 80 + rand()%120;
	
	for(i=0; i<l; i++)
		message[i] = (char) 32 + rand() % 95;
		
	message[i] = '\0';
	
	printf("%s\n", message);
		
	tid = (pthread_t*) malloc(thread_qty * sizeof(pthread_t*));
	semaf = malloc(thread_qty * sizeof(sem_t));
	
	for(i=0; i<thread_qty; i++)
	{
		sem_init(&semaf[i], 0, !i);
		pthread_create(&tid[i], NULL, thread_mess, (void*) i);
	}
	
	for(i=0; i<thread_qty; i++)
		pthread_join(tid[i], NULL);
		
	printf("%s\n",message);
	
}
