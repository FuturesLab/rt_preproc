#include <stdio.h>      /* printf */

#ifdef FOO
  void func(){ printf("FOO defined func!"); }
#else
  void func(){ printf("FOO not defined func!"); }
#endif 
 
int main(){
  func();
}
