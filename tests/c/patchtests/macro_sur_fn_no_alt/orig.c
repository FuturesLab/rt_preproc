#include <stdio.h>      /* printf */

#ifdef FOO
  void func(){ printf("FOO defined func!"); }
#endif 
 
int main(){
  func();
}
