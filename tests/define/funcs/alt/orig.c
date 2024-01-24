#include <stdio.h>      /* printf */

#ifdef FOO
  #define MAX(a,b) ((a) > (b) ? (a) : (b))
#else
  #define MAX(a,b) ((a) < (b) ? (a) : (b))
#endif
 
int main(){
  int x = MAX(1, 4);
  printf("%d", x);
}
