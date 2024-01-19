#include <stdio.h>      /* printf */

#ifdef FOO
  int func(){ return 1; }
#else
  int func(){ return 2; }
#endif 
 
int main(){
  int x = func();
  printf("%d ", x);
  printf("%d", func());
}
