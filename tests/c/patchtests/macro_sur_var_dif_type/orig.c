#include <stdio.h>      /* printf */

#ifdef FOO
  int x;
#else 
  char x;
#endif

#ifdef FOO
  int func(int val) {
    return val + 1;
  }
#else
  char func(char val) {
    return val;
  }
#endif
 
int main(){
  #ifdef FOO
    printf("%d", func(3));
  #else
    printf("%c", func(3));
  #endif
}
