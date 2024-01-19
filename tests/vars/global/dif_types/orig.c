#include <stdio.h>      /* printf */

#ifdef FOO
  int x = 2;
#else 
  char x = 'a';
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
    printf("%d", func(x));
  #else
    printf("%c", func(x));
  #endif
}
