#include <stdio.h>

int main()
{
	#ifdef A
	#ifdef B
	#ifdef C
	print("foo");
	#endif
	#endif
	#endif
	return 0;
}