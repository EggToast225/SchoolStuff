#include <stdio.h>

int main()
{
    int size; 
    scanf("%d", &size);
    
    int sum = 0;
    int array[size];
    for(int i = 0; i < size; i++){
        scanf("%d", &array[i]);
    }
    
    for(int i = 0; i < size; i++){
        sum += array[i];
    }
    
    printf("%d", sum);
    return 0;
}