#include <stdio.h>

int main()
{
    int size;
    scanf("%d", &size);
    
    int array1[size];
    int array2[size];
    for(int i = 0; i < size; i++){
        scanf("%d %d", &array1[i], &array2[i]);
    }
    for(int i = 0; i < size; i++){
        if (array1[i] < array2[i]){
            printf("%d ",array1[i]);
            continue;
        }
        printf("%d ", array2[i]);
    };
    
    

    return 0;
}