#include <stdio.h>      /* printf */

#ifdef FOO
  int val = 10;
#else
  char val = 'a';
#endif

#ifdef FOO
  void func(int x){ printf("FOO defined func! %d", x); }
#else
  void func(char x){ printf("FOO not defined func! %c", x); }
#endif 


 
int main(){
  func(val);
}
