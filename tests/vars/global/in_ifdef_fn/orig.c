#include <stdio.h>      /* printf */

#ifdef FOO
  int var = 1;
#endif

#ifdef FOO
  int func(){ return var; }
#else
  int func(){ return 2; }
#endif 
 
int main(){
  int x = func();
  x += var;
  printf("%d ", x);
}
